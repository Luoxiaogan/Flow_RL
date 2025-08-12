# Workflow ID: high_level_math_ganluo_21_0
# Benchmark: high_level_math_ganluo
# Data Indices: [9]

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

        # Step 1: Extract and understand the problem
        problem_breakdown = await self.generate(
            instruction="Carefully analyze the problem statement. Identify all given constraints, variables, and what is being asked. Provide a structured breakdown of the problem.",
            context=self.problem_text
        )

        # Step 2: Generate multiple candidate solutions in parallel
        results = await asyncio.gather(
            self.generate(
                instruction=f"Using the problem breakdown: {problem_breakdown}\nSolve the problem using a combinatorial approach. Provide detailed reasoning and calculations.",
                context=self.problem_text
            ),
            self.generate(
                instruction=f"Using the problem breakdown: {problem_breakdown}\nSolve the problem using an algebraic approach. Provide detailed reasoning and calculations.",
                context=self.problem_text
            ),
            self.generate(
                instruction=f"Using the problem breakdown: {problem_breakdown}\nSolve the problem using a geometric or visual approach. Provide detailed reasoning and calculations.",
                context=self.problem_text
            )
        )

        # Step 3: Refine each candidate solution
        refined_solutions = await asyncio.gather(
            self.revise(
                instruction="Critique and improve the following solution. Ensure it satisfies all constraints and is mathematically rigorous.",
                context=results[0]
            ),
            self.revise(
                instruction="Critique and improve the following solution. Ensure it satisfies all constraints and is mathematically rigorous.",
                context=results[1]
            ),
            self.revise(
                instruction="Critique and improve the following solution. Ensure it satisfies all constraints and is mathematically rigorous.",
                context=results[2]
            )
        )

        # Step 4: Select the best solution using Ensemble
        best_solution = await self.ensemble(
            instruction="Compare the following solutions. Evaluate their correctness, efficiency, and adherence to the problem constraints. Select the best solution.",
            contexts=refined_solutions
        )

        # Step 5: Extract and format the final answer
        final_answer = await self.summarize(
            instruction="Extract the final answer from the selected solution. Ensure it is in the required format and satisfies all problem constraints.",
            context=best_solution
        )

        return final_answer