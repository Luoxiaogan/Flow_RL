# Workflow ID: humaneval_49_0
# Benchmark: humaneval
# Data Indices: [160, 39]

class Workflow:
    def __init__(self, config, problem) -> None:
        self.config = config
        self.problem_text = problem
        self.llm = create(config)
        
        self.generate = operator.Generate(self.llm, self.problem_text)
        self.revise = operator.Revise(self.llm, self.problem_text)
        self.summarize = operator.Summarize(self.llm, self.problem_text)
        self.ensemble = operator.Ensemble(self.llm, self.problem_text)

    async def run_workflow(self):
        import asyncio
        import re

        # PHASE 1: STRUCTURAL DECOMPOSITION & CLASSIFICATION
        problem_analysis = await self.generate(
            instruction="""Perform deep structural analysis of the problem:
            1. Extract the exact function signature and ENTRY POINT name.
            2. Identify input/output types from examples and docstring.
            3. Classify problem type: 
               - Is it expression evaluation? 
               - Sequence generation with filtering? 
               - String/list manipulation? 
               - Mathematical formula?
               - Recursive/iterative algorithm?
            4. List all operators, constraints, and edge cases mentioned or implied.
            5. Note any special handling required (e.g., integer vs float, operator precedence).
            Format as structured JSON-like text with clear sections.""",
            context=""
        )

        # PHASE 2: PARALLEL STRATEGY GENERATION
        strategy_tasks = [
            self.generate(
                instruction=f"""Generate solution using DIRECT EXAMPLE MIMICRY strategy:
                - Study the provided examples in docstring.
                - Replicate their structure and logic exactly.
                - Do not generalize beyond what examples demonstrate.
                - Prioritize simplicity and literal interpretation.
                - Use the exact function name from ENTRY POINT.
                Problem context: {problem_analysis}""",
                context=""
            ),
            self.generate(
                instruction=f"""Generate solution using ALGORITHMIC GENERALIZATION strategy:
                - Derive underlying algorithm or formula from examples.
                - Implement generalized solution that handles all cases.
                - Include proper edge case handling.
                - Avoid eval() or unsafe operations unless explicitly shown in examples.
                - Use the exact function name from ENTRY POINT.
                Problem context: {problem_analysis}""",
                context=""
            ),
            self.generate(
                instruction=f"""Generate solution using SAFE/EXPLICIT COMPUTATION strategy:
                - Avoid eval(), exec(), or any dynamic code execution.
                - Use explicit step-by-step computation.
                - Handle operator precedence manually if needed.
                - Include detailed comments for clarity.
                - Ensure type correctness (int vs float) as shown in examples.
                - Use the exact function name from ENTRY POINT.
                Problem context: {problem_analysis}""",
                context=""
            )
        ]
        
        strategy_candidates = await asyncio.gather(*strategy_tasks)

        # PHASE 3: CONSTRAINT-AWARE REVISION
        revision_tasks = []
        for i, candidate in enumerate(strategy_candidates):
            revision_instruction = f"""REVISE this solution candidate:
            - Ensure function name matches ENTRY POINT EXACTLY.
            - Verify return type matches examples (int, float, str, etc.).
            - Add handling for edge cases mentioned in problem_analysis.
            - Remove any unnecessary code or over-engineering.
            - If using eval(), ensure it's safe and matches example patterns.
            - Code must be minimal and directly solve the specification.
            - Double-check operator precedence and mathematical correctness.
            Problem context: {problem_analysis}
            """
            revision_tasks.append(
                self.revise(instruction=revision_instruction, context=candidate)
            )
        
        revised_candidates = await asyncio.gather(*revision_tasks)

        # PHASE 4: ENSEMBLE SYNTHESIS WITH META-VALIDATION
        final_solution = await self.ensemble(
            instruction="""SYNTHESIZE the best solution from all candidates:
            - Combine the safest, most correct elements from each.
            - Prioritize solutions that handle edge cases explicitly.
            - Favor minimal, readable code that matches example style.
            - Ensure function name is exactly as specified in ENTRY POINT.
            - Return type must be consistent with all examples.
            - If multiple correct solutions exist, choose the most efficient.
            - Output ONLY the final Python function code, nothing else.""",
            contexts_list=revised_candidates
        )

        # PHASE 5: ADVERSARIAL FEEDBACK LOOP (MAX 2 ITERATIONS)
        current_solution = final_solution
        for iteration in range(2):
            validation_feedback = await self.generate(
                instruction=f"""Act as a HIDDEN TEST CASE VALIDATOR:
                - What edge cases or inputs might break this solution?
                - Are there type mismatches or off-by-one errors?
                - Does it handle all operators/constraints from problem_analysis?
                - Is the function name exact?
                - Would it fail on the provided examples?
                Return ONLY specific, actionable criticisms or 'PASSED' if flawless.
                Current solution: {current_solution}
                Problem context: {problem_analysis}""",
                context=current_solution
            )
            
            if "PASSED" in validation_feedback.upper() or "NO ISSUES" in validation_feedback.upper():
                break
                
            current_solution = await self.revise(
                instruction=f"""FIX the solution based on validator feedback:
                - Address ALL issues raised in feedback.
                - Maintain function name and return type.
                - Keep code minimal and example-aligned.
                Validator feedback: {validation_feedback}
                Problem context: {problem_analysis}""",
                context=current_solution
            )

        return current_solution