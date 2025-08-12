# Workflow ID: high_level_math_ganluo_0_0
# Benchmark: high_level_math_ganluo
# Data Indices: [27]

class Workflow:
    def __init__(self, config, problem) -> None:
        # --- DO NOT MODIFY THIS SECTION ---
        self.config = config
        self.problem_text = problem
        self.llm = create(config)
        
        self.generate = operator.Generate(self.llm, self.problem_text)
        self.revise = operator.Revise(self.llm, self.llm, self.problem_text)
        self.summarize = operator.Summarize(self.llm, self.problem_text)
        self.ensemble = operator.Ensemble(self.llm, self.problem_text)

    async def run_workflow(self):
        """
        Implement the core problem-solving logic here.
        """
        import asyncio

        # Step 1: Problem Analysis and Key Extraction
        analysis_instruction = (
            "Analyze the problem statement to identify the sequence definition, "
            "initial conditions, and target. Extract all numerical values, recursive formulas, "
            "and constraints. Focus on understanding the mathematical structure."
        )
        analysis = await self.generate(instruction=analysis_instruction, context=self.problem_text)

        # Step 2: Pattern Recognition and Simplification
        pattern_instruction = (
            f"Given the extracted information: {analysis}, analyze the recursive formula. "
            "Determine if the sequence converges, exhibits periodic behavior, or has invariants. "
            "Simplify the sequence into a manageable form if possible."
        )
        pattern_analysis = await self.generate(instruction=pattern_instruction, context=self.problem_text)

        # Step 3: Computation and Generalization
        computation_instruction = (
            f"Using the simplified sequence: {pattern_analysis}, compute terms iteratively "
            "or derive a closed-form expression. Handle large indices efficiently using patterns "
            "or modular arithmetic. Ensure the solution is scalable for large indices like 2025."
        )
        computation_results = await asyncio.gather(
            self.generate(instruction=computation_instruction, context=self.problem_text),
            self.generate(instruction="Propose an alternative computational approach.", context=self.problem_text)
        )

        # Step 4: Ensemble to Select Best Solution Path
        ensemble_instruction = (
            "Evaluate the provided computational results. Select the most efficient and accurate "
            "approach for solving the sequence. Ensure the chosen method aligns with the problem's constraints."
        )
        best_solution = await self.ensemble(instruction=ensemble_instruction, contexts=computation_results)

        # Step 5: Number Theory and Final Calculation
        number_theory_instruction = (
            f"Given the computed result: {best_solution}, express it as a fraction m/n where m and n "
            "are relatively prime. Perform modular arithmetic to compute the remainder when m + n is "
            "divided by 1000."
        )
        final_result = await self.generate(instruction=number_theory_instruction, context=self.problem_text)

        # Step 6: Refinement and Verification
        refinement_instruction = (
            "Review the final result for accuracy. Verify that all constraints are satisfied, "
            "including the format of the answer and the modular arithmetic calculation."
        )
        refined_result = await self.revise(instruction=refinement_instruction, context=final_result)

        return refined_result