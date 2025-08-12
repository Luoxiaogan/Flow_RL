# Workflow ID: high_level_math_ganluo_24_0
# Benchmark: high_level_math_ganluo
# Data Indices: [18]

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
        Implement the core problem-solving logic here.
        """
        import asyncio

        # Step 1: Extract key components from the problem
        extraction = await self.generate(
            instruction="Extract all variables, constants, and operations from the problem. "
                        "Identify any constraints or conditions explicitly stated. "
                        "Focus on understanding the structure of the mathematical expression.",
            context=self.problem_text
        )

        # Step 2: Generate multiple solution approaches
        approach1 = self.generate(
            instruction=f"Given the extracted components: {extraction}, "
                        "solve the problem algebraically by simplifying the logarithmic expressions. "
                        "Look for patterns such as telescoping products or recursive relationships.",
            context=self.problem_text
        )
        approach2 = self.generate(
            instruction=f"Given the extracted components: {extraction}, "
                        "approach the problem numerically by approximating intermediate values. "
                        "Verify if the numerical results align with the algebraic structure.",
            context=self.problem_text
        )
        approach3 = self.generate(
            instruction=f"Given the extracted components: {extraction}, "
                        "explore combinatorial or number-theoretic techniques to simplify the problem. "
                        "Check for divisibility, modular arithmetic, or symmetry properties.",
            context=self.problem_text
        )

        # Execute approaches in parallel
        results = await asyncio.gather(approach1, approach2, approach3)

        # Step 3: Evaluate and select the best approach
        best_solution = await self.ensemble(
            instruction="Compare the following candidate solutions. "
                        "Select the most mathematically rigorous and efficient approach. "
                        "Ensure the chosen solution satisfies all constraints and conditions.",
            contexts=results
        )

        # Step 4: Refine the selected solution
        refined_solution = await self.revise(
            instruction="Critique and refine the selected solution. "
                        "Ensure all steps are clear, logical, and mathematically sound. "
                        "Correct any errors or ambiguities.",
            context=best_solution
        )

        # Step 5: Summarize the final answer
        final_answer = await self.summarize(
            instruction="Condense the refined solution into a concise summary. "
                        "Present the final answer in the required format, such as m + n for fractions.",
            context=refined_solution
        )

        return final_answer