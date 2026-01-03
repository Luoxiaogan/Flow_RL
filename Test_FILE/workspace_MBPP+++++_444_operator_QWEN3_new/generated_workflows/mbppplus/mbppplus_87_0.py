# Workflow ID: mbppplus_87_0
# Benchmark: mbppplus
# Data Indices: [305, 25, 118]

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
        import json

        # Phase 1: Problem Classification and Edge Case Identification
        classification = await self.generate(
            instruction="""Thoroughly analyze the problem to determine:
            1. Primary category: Is this a string manipulation, mathematical computation, data structure operation, or logical validation problem?
            2. Expected input types and output types (be specific: list, tuple, string, number, etc.)
            3. Critical edge cases: What boundary conditions must be handled? (e.g., empty inputs, zero, negatives, malformed data)
            4. Algorithmic approach: What kind of solution is likely required? (regex, arithmetic formula, iteration, recursion, etc.)
            5. Return value constraints: Are there specific formats or error codes to return?
            Provide a structured JSON-like analysis with clear sections for each point above.""",
            context=""
        )

        # Phase 2: Parallel Solution Generation - Generate multiple approaches
        solution_attempts = await asyncio.gather(
            self.generate(
                instruction=f"""Based on this classification:
                {classification}
                
                Generate a complete Python function implementation that solves the problem.
                Approach 1: Focus on simplicity and direct implementation. Handle edge cases as identified.
                Include all necessary imports. Match the exact function signature. Return correct data types.
                Write clean, efficient code with clear variable names.""",
                context=classification
            ),
            self.generate(
                instruction=f"""Based on this classification:
                {classification}
                
                Generate a complete Python function implementation that solves the problem.
                Approach 2: Focus on robustness and comprehensive edge case handling. Be defensive.
                Include all necessary imports. Match the exact function signature. Return correct data types.
                Consider alternative algorithms or more thorough validation than Approach 1.""",
                context=classification
            ),
            self.generate(
                instruction=f"""Based on this classification:
                {classification}
                
                Generate a complete Python function implementation that solves the problem.
                Approach 3: Focus on efficiency and elegance. Use the most appropriate Python idioms.
                Include all necessary imports. Match the exact function signature. Return correct data types.
                Prioritize readability and Pythonic style while ensuring correctness.""",
                context=classification
            )
        )

        # Phase 3: Parallel Validation and Critique
        critiques = await asyncio.gather(
            *[self.revise(
                instruction=f"""Critically evaluate this solution:
                - Does it handle all edge cases identified in classification?
                - Does it match expected input/output types?
                - Are there any logical errors or boundary condition oversights?
                - Is the code efficient and readable?
                - Does it include necessary imports and match function signature?
                Provide specific, actionable feedback. If no issues, state "No issues found."
                Classification context: {classification}""",
                context=solution
            ) for solution in solution_attempts]
        )

        # Phase 4: Iterative Refinement Loop (max 3 iterations)
        refined_solutions = solution_attempts.copy()
        for iteration in range(3):
            # Check if any critique found critical issues
            has_critical_issues = any("error" in critique.lower() or "missing" in critique.lower() or "wrong" in critique.lower() for critique in critiques)
            
            if not has_critical_issues:
                break  # No critical issues found, exit early
                
            # Refine solutions with issues
            refinement_tasks = []
            for i, (solution, critique) in enumerate(zip(refined_solutions, critiques)):
                if "No issues found." in critique:
                    refinement_tasks.append(asyncio.create_task(asyncio.sleep(0, result=solution)))  # Keep unchanged
                else:
                    refinement_tasks.append(asyncio.create_task(self.revise(
                        instruction=f"""Revise this solution based on the critique:
                        {critique}
                        
                        Fix all identified issues while preserving the core logic.
                        Ensure edge cases are handled, types are correct, and function signature is matched.
                        Maintain clean, efficient code. Include necessary imports.
                        Classification context: {classification}""",
                        context=solution
                    )))
            
            refined_solutions = await asyncio.gather(*refinement_tasks)
            
            # Re-critique refined solutions
            critiques = await asyncio.gather(
                *[self.revise(
                    instruction=f"""Critically evaluate this revised solution:
                    - Have all previous issues been addressed?
                    - Are there any new issues introduced?
                    - Does it now handle all edge cases?
                    - Is the code correct and efficient?
                    Classification context: {classification}""",
                    context=solution
                ) for solution in refined_solutions]
            )

        # Phase 5: Ensemble Selection and Synthesis
        final_solution = await self.ensemble(
            instruction="""Select the best solution from the candidates below, or synthesize a new one combining the best elements of each.
            Selection criteria:
            1. Correctness: Handles all edge cases and produces right outputs
            2. Robustness: Gracefully handles unexpected inputs
            3. Efficiency: Uses appropriate algorithms without unnecessary complexity
            4. Readability: Clean, well-structured code with good variable names
            5. Completeness: Includes necessary imports, matches function signature exactly
            
            If one solution is clearly superior, select it. If multiple have complementary strengths, create a synthesized version.
            Return ONLY the final Python function code with imports, nothing else.""",
            contexts_list=refined_solutions
        )

        return final_solution