# Workflow ID: mbppplus_86_0
# Benchmark: mbppplus
# Data Indices: [359, 141, 69]

# --- DO NOT IMPORT HERE ---
class Workflow:
    def __init__(self, config, problem) -> None:
        # --- DO NOT MODIFY THIS SECTION ---
        self.config = config
        self.problem_text = problem
        self.llm = create(config)
        
        self.generate = operator.Generate(self.llm, self.problem_text)
        self.revise = operator.Revise(self.llm, self.problem_text)
        self.summarize = operator.Summarize(self.llm, self.problem_text)
        self.ensemble = operator.Ensemble(self.llm, self.problem_text)

    async def run_workflow(self):
        """
        Universal workflow for algorithmic programming problems.
        Uses parallel strategy generation, ensemble synthesis, and iterative refinement.
        """
        import asyncio

        # Step 1: Deep problem analysis - extract intent, constraints, edge cases
        problem_analysis = await self.generate(
            instruction="""Thoroughly analyze the programming problem. 
            - What is the exact purpose of the function? 
            - What are the input parameters and expected output type?
            - What are the implicit and explicit constraints?
            - What edge cases must be handled (empty inputs, zeros, negatives, boundaries)?
            - Are there any mathematical formulas or algorithmic patterns involved?
            - What would cause the solution to fail?
            Do not write code yet. Focus on complete problem understanding.""",
            context=""
        )

        # Step 2: Parallel strategy generation - explore 3 different solution approaches
        strategy_tasks = [
            self.generate(
                instruction=f"""Based on this analysis: {problem_analysis}
                Propose a mathematical/formula-based solution.
                - Use direct computation if possible
                - Include necessary imports (math, etc.)
                - Handle edge cases explicitly
                - Return correct data type
                - Write clean, efficient code
                Justify why this approach is valid.""",
                context=problem_analysis
            ),
            self.generate(
                instruction=f"""Based on this analysis: {problem_analysis}
                Propose an iterative/algorithmic solution.
                - Use loops or accumulators if appropriate
                - Handle edge cases explicitly
                - Return correct data type
                - Write clean, efficient code
                Justify why this approach is valid.""",
                context=problem_analysis
            ),
            self.generate(
                instruction=f"""Based on this analysis: {problem_analysis}
                Propose a recursive/logical solution.
                - Use recursion or functional decomposition if appropriate
                - Handle base cases and edge cases
                - Return correct data type
                - Write clean, efficient code
                Justify why this approach is valid.""",
                context=problem_analysis
            )
        ]
        
        strategy_proposals = await asyncio.gather(*strategy_tasks)

        # Step 3: Ensemble synthesis - combine best elements or select optimal solution
        synthesized_solution = await self.ensemble(
            instruction="""Compare these three solution proposals.
            - Which one is most correct and handles all edge cases?
            - Which is most efficient and readable?
            - Are there elements from multiple solutions that should be combined?
            - Are there any remaining flaws or missing cases?
            Synthesize the best possible solution. 
            Output ONLY the final Python function implementation with any necessary imports.
            Ensure it matches the required function signature exactly.
            Handle all edge cases identified in the analysis.""",
            contexts_list=strategy_proposals
        )

        # Step 4: Critical revision - fix any remaining issues
        final_solution = await self.revise(
            instruction="""Critically examine this code:
            - Does it handle ALL edge cases (empty, zero, negative, boundary)?
            - Is the return type exactly as required?
            - Are there any logical errors or off-by-one mistakes?
            - Are variable names clear and imports included?
            - Would it pass the sample test cases?
            Fix any issues found. Improve clarity and robustness.
            Output ONLY the corrected Python function implementation.
            Do not add explanations or markdown.""",
            context=synthesized_solution
        )

        # Step 5: Validation check and optional re-revision
        validation_check = await self.generate(
            instruction="""Does this code contain any obvious errors, missing imports, 
            or logical flaws? Check for:
            - Syntax errors
            - Undefined variables
            - Missing edge case handling
            - Incorrect return types
            - Mathematical inaccuracies
            If any issues are found, describe them concisely. Otherwise, output 'VALID'.""",
            context=final_solution
        )

        # If validation finds issues, do one final revision
        if "error" in validation_check.lower() or "missing" in validation_check.lower() or "invalid" in validation_check.lower():
            final_solution = await self.revise(
                instruction=f"""Fix the following issues: {validation_check}
                Output ONLY the corrected Python function implementation.
                Ensure it's production-ready and handles all edge cases.""",
                context=final_solution
            )

        return final_solution