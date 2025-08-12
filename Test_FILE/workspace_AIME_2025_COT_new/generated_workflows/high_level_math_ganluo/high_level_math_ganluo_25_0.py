# Workflow ID: high_level_math_ganluo_25_0
# Benchmark: high_level_math_ganluo
# Data Indices: [25]

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

        # Step 1: Problem Understanding and Key Information Extraction
        problem_summary = await self.generate(
            instruction="Extract and summarize the key information from the problem, including the geometric object, constraints, and requirements. Provide a clear breakdown of what is being asked.",
            context=self.problem_text
        )

        # Step 2: Generate Multiple Solution Strategies
        strategy_1 = await self.generate(
            instruction=f"Using symmetry arguments, propose a solution strategy for the problem. Consider how symmetries in the geometric object can simplify the counting process. Problem summary: {problem_summary}",
            context=self.problem_text
        )
        strategy_2 = await self.generate(
            instruction=f"Using combinatorial enumeration, propose a solution strategy for the problem. Focus on systematically counting valid configurations. Problem summary: {problem_summary}",
            context=self.problem_text
        )
        strategy_3 = await self.generate(
            instruction=f"Using recursive reasoning, propose a solution strategy for the problem. Consider how smaller cases can build up to the full solution. Problem summary: {problem_summary}",
            context=self.problem_text
        )

        # Step 3: Evaluate and Select the Best Strategy
        best_strategy = await self.ensemble(
            instruction="Evaluate the provided strategies and select the most mathematically rigorous, computationally feasible, and aligned with the problem constraints. Provide a justification for your choice.",
            contexts=[strategy_1, strategy_2, strategy_3]
        )

        # Step 4: Execute the Chosen Strategy
        detailed_solution = await self.generate(
            instruction=f"Execute the chosen strategy step by step. Ensure all constraints are satisfied and intermediate results are verified. Best strategy: {best_strategy}",
            context=self.problem_text
        )
        refined_solution = await self.revise(
            instruction="Critique and refine the detailed solution. Ensure clarity, correctness, and alignment with the problem requirements.",
            context=detailed_solution
        )

        # Step 5: Final Verification and Presentation
        final_answer = await self.summarize(
            instruction="Summarize the refined solution and present the final answer. Ensure the result is concise, correct, and satisfies all problem constraints.",
            context=refined_solution
        )

        return final_answer