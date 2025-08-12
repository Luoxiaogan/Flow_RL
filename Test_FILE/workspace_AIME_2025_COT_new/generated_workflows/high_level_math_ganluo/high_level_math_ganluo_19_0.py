# Workflow ID: high_level_math_ganluo_19_0
# Benchmark: high_level_math_ganluo
# Data Indices: [26]

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

        # Step 1: Extract key information and constraints
        extraction = await self.generate(
            instruction="Extract all numerical values, geometric relationships, and constraints from the problem. "
                        "Identify the target expression to compute and any specific formatting requirements.",
            context=self.problem_text
        )

        # Step 2: Generate multiple solution approaches
        approach_1 = await self.generate(
            instruction=f"Using the extracted information: {extraction}, "
                        "solve the problem using coordinate geometry. Represent the vertices of the polygon in a coordinate system, "
                        "and calculate the required distances and angles.",
            context=self.problem_text
        )
        approach_2 = await self.generate(
            instruction=f"Using the extracted information: {extraction}, "
                        "solve the problem using trigonometric identities. Focus on the given cosine values and triangle areas "
                        "to derive expressions for the side lengths and angles.",
            context=self.problem_text
        )
        approach_3 = await self.generate(
            instruction=f"Using the extracted information: {extraction}, "
                        "solve the problem using synthetic geometry. Analyze the geometric properties of the polygon "
                        "and use symmetry or other geometric insights to simplify the calculations.",
            context=self.problem_text
        )

        # Step 3: Refine each approach
        refined_1 = await self.revise(
            instruction="Critique and improve the coordinate geometry solution. Ensure all calculations are correct "
                        "and align with the problem constraints.",
            context=approach_1
        )
        refined_2 = await self.revise(
            instruction="Critique and improve the trigonometric solution. Verify the derived expressions for side lengths "
                        "and angles using the given cosine values and triangle areas.",
            context=approach_2
        )
        refined_3 = await self.revise(
            instruction="Critique and improve the synthetic geometry solution. Ensure the reasoning is rigorous "
                        "and accounts for all geometric properties of the polygon.",
            context=approach_3
        )

        # Step 4: Summarize each refined approach
        summary_1 = await self.summarize(
            instruction="Summarize the refined coordinate geometry solution, highlighting the key steps and results.",
            context=refined_1
        )
        summary_2 = await self.summarize(
            instruction="Summarize the refined trigonometric solution, focusing on the derived expressions and their validity.",
            context=refined_2
        )
        summary_3 = await self.summarize(
            instruction="Summarize the refined synthetic geometry solution, emphasizing the geometric insights used.",
            context=refined_3
        )

        # Step 5: Ensemble decision to select the best approach
        final_solution = await self.ensemble(
            instruction="Compare the three summarized solutions. Select the most rigorous, accurate, and efficient approach. "
                        "Synthesize the best solution into a final answer, ensuring it satisfies all problem constraints.",
            contexts=[summary_1, summary_2, summary_3]
        )

        # Step 6: Final verification and formatting
        verified_solution = await self.revise(
            instruction="Verify the final solution against all problem constraints. Ensure the result is correctly formatted "
                        "as specified in the problem (e.g., simplified fractions, radicals).",
            context=final_solution
        )

        return verified_solution