# Workflow ID: humaneval_19_0
# Benchmark: humaneval
# Data Indices: [116, 51]

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

        # STAGE 1: PROBLEM DECOMPOSITION & CLASSIFICATION
        decomposition = await self.generate(
            instruction="""Thoroughly decompose the problem specification:
            1. Extract the exact function signature and ENTRY POINT name.
            2. Parse all examples from the docstring - identify inputs and expected outputs.
            3. Classify the problem type: string manipulation, mathematical, sorting, filtering, etc.
            4. Identify explicit and implicit constraints (e.g., edge cases like empty input, negative numbers).
            5. Note any inconsistencies or ambiguities in the examples.
            6. Determine the core algorithmic pattern required.
            Present your analysis in structured sections with clear headings.""",
            context=""
        )

        # STAGE 2: PARALLEL STRATEGY GENERATION
        strategy_tasks = [
            self.generate(
                instruction=f"""Generate a Python function implementation based on this strategy:
                STRATEGY: Use built-in Python functions and idioms for maximum simplicity.
                GUIDELINES:
                - Match the ENTRY POINT function name exactly.
                - Handle all edge cases identified in decomposition.
                - Return types must match examples precisely.
                - Prefer list comprehensions, sorted() with key, or string methods when applicable.
                - No extra imports unless absolutely necessary.
                - Code must be self-contained and directly executable.
                Context from problem decomposition:
                {decomposition}""",
                context=decomposition
            ),
            self.generate(
                instruction=f"""Generate a Python function implementation based on this strategy:
                STRATEGY: Manual implementation with explicit loops and conditionals for maximum control.
                GUIDELINES:
                - Match the ENTRY POINT function name exactly.
                - Handle all edge cases identified in decomposition.
                - Return types must match examples precisely.
                - Avoid built-in functions that abstract away core logic (e.g., use manual counting instead of .count()).
                - Code must be self-contained and directly executable.
                Context from problem decomposition:
                {decomposition}""",
                context=decomposition
            ),
            self.generate(
                instruction=f"""Generate a Python function implementation based on this strategy:
                STRATEGY: Optimized and pythonic, using advanced features like lambda, generators, or itertools if beneficial.
                GUIDELINES:
                - Match the ENTRY POINT function name exactly.
                - Handle all edge cases identified in decomposition.
                - Return types must match examples precisely.
                - Use the most elegant and efficient Python constructs available.
                - Code must be self-contained and directly executable.
                Context from problem decomposition:
                {decomposition}""",
                context=decomposition
            )
        ]
        
        strategy_candidates = await asyncio.gather(*strategy_tasks)

        # STAGE 3: VALIDATION SIMULATION
        validation_tasks = []
        for i, candidate in enumerate(strategy_candidates):
            validation = await self.generate(
                instruction=f"""Simulate the execution of this candidate solution against ALL examples from the specification:
                CANDIDATE {i+1}:
                {candidate}
                
                For each example:
                1. Trace through the code step by step.
                2. Predict the output.
                3. Compare with expected output from specification.
                4. Identify any mismatches or edge cases not handled.
                5. Assess code structure: correct function name? Correct return type?
                Provide a detailed validation report with 'PASS' or 'FAIL' for each example.""",
                context=candidate
            )
            validation_tasks.append(validation)
        
        validation_results = await asyncio.gather(*validation_tasks)

        # STAGE 4: ENSEMBLE SELECTION
        selected_solution = await self.ensemble(
            instruction="""Select the best solution based on:
            1. Correctness: Which solution passes all example simulations?
            2. Simplicity: Prefer concise, readable code.
            3. Robustness: Which handles edge cases most thoroughly?
            4. Fidelity: Exact match to function name and return types.
            If multiple solutions are correct, choose the most pythonic.
            If none are fully correct, select the one closest to correct and note what needs fixing.
            Return ONLY the selected code block, nothing else.""",
            contexts_list=[f"Candidate {i+1}:\n{candidate}\n\nValidation:\n{validation}" 
                          for i, (candidate, validation) in enumerate(zip(strategy_candidates, validation_results))]
        )

        # STAGE 5: ADVERSARIAL REFINEMENT
        refined_solution = await self.revise(
            instruction=f"""Critically examine this solution for potential failures:
            {selected_solution}
            
            Apply adversarial testing:
            1. What edge cases might still be unhandled? (None, empty, max values, unicode, etc.)
            2. Could return types be mismatched? (list vs tuple, int vs float)
            3. Is the function name exactly as specified in ENTRY POINT?
            4. Are there any off-by-one errors or boundary condition flaws?
            5. Could performance be an issue for large inputs?
            Revise the code to address all identified weaknesses.
            Preserve the exact function signature and ENTRY POINT name.
            Return only the improved code.""",
            context=selected_solution
        )

        # STAGE 6: FINAL COMPLIANCE CHECK
        final_solution = await self.revise(
            instruction=f"""Perform final compliance verification:
            {refined_solution}
            
            CHECKLIST:
            1. Function name matches ENTRY POINT exactly.
            2. Code is syntactically valid Python.
            3. Return types match examples precisely.
            4. All examples from specification are handled correctly.
            5. No unnecessary imports or helper functions.
            6. Code is self-contained and directly executable.
            If any item fails, fix it immediately.
            Return ONLY the final compliant code, nothing else.""",
            context=refined_solution
        )

        return final_solution