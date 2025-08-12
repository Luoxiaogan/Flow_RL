# Workflow ID: high_level_math_ganluo_4_0
# Benchmark: high_level_math_ganluo
# Data Indices: [24]

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

        # Step 1: Extract problem details and constraints
        extraction = await self.generate(
            instruction="Extract all key details from the problem, including numerical values, constraints, "
                        "and any patterns or symmetries. Focus on understanding the mathematical structure "
                        "and the type of combinatorial problem being posed.",
            context=self.problem_text
        )

        # Step 2: Generate multiple solution approaches in parallel
        approach1 = self.generate(
            instruction=f"Using casework analysis, solve the problem step by step. Consider all possible "
                        f"cases based on the extracted details: {extraction}. Ensure each case satisfies "
                        f"all constraints and compute the total count.",
            context=self.problem_text
        )
        approach2 = self.generate(
            instruction=f"Develop a recursive formula to solve the problem. Use the extracted details: {extraction} "
                        f"to define base cases and recurrence relations. Compute the total count using this formula.",
            context=self.problem_text
        )
        approach3 = self.generate(
            instruction=f"Use generating functions to model the problem. Based on the extracted details: {extraction}, "
                        f"construct the appropriate generating function and compute the coefficient corresponding "
                        f"to the desired count.",
            context=self.problem_text
        )

        # Execute approaches in parallel
        results = await asyncio.gather(approach1, approach2, approach3)

        # Step 3: Ensemble decision-making to select or synthesize the best solution
        ensemble_result = await self.ensemble(
            instruction="Compare the following candidate solutions. Evaluate their logical consistency, "
                        "mathematical rigor, and computational feasibility. Select the best solution or synthesize "
                        "a new one if necessary.",
            contexts=results
        )

        # Step 4: Refine the selected solution for clarity and correctness
        refined_solution = await self.revise(
            instruction="Review the selected solution for any errors, ambiguities, or missing steps. "
                        "Ensure all constraints are satisfied and the reasoning is clear and rigorous. "
                        "If necessary, rewrite parts of the solution for better clarity.",
            context=ensemble_result
        )

        # Step 5: Summarize the final answer in the required format
        final_answer = await self.summarize(
            instruction="Extract the final numerical answer from the refined solution. If the problem "
                        "requires a specific format (e.g., remainder when divided by 1000), compute and "
                        "present the result accordingly.",
            context=refined_solution
        )

        return final_answer