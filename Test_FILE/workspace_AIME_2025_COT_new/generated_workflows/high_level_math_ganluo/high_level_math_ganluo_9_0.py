# Workflow ID: high_level_math_ganluo_9_0
# Benchmark: high_level_math_ganluo
# Data Indices: [16]

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

        # Step 1: Extract key information and understand the problem
        extraction = await self.generate(
            instruction="Extract all key mathematical elements from the problem, including variables, equations, constraints, and relationships. Summarize the problem's requirements clearly.",
            context=self.problem_text
        )

        # Step 2: Strategically decompose the problem into sub-problems
        strategy = await self.generate(
            instruction=f"Based on the extracted information: {extraction}, outline potential solution paths. Consider techniques like casework analysis, modular arithmetic, symmetry exploitation, and algebraic manipulation.",
            context=self.problem_text
        )

        # Step 3: Explore multiple solution paths in parallel
        approach_1 = self.generate(
            instruction=f"Using the outlined strategy: {strategy}, solve the problem using algebraic manipulation and simplification.",
            context=self.problem_text
        )
        approach_2 = self.generate(
            instruction=f"Using the outlined strategy: {strategy}, solve the problem using number-theoretic properties and divisibility analysis.",
            context=self.problem_text
        )
        approach_3 = self.generate(
            instruction=f"Using the outlined strategy: {strategy}, solve the problem using combinatorial reasoning or recursive structures if applicable.",
            context=self.problem_text
        )

        # Execute approaches in parallel
        results = await asyncio.gather(approach_1, approach_2, approach_3)

        # Step 4: Evaluate and synthesize results
        best_solution = await self.ensemble(
            instruction="Compare the provided solutions and select the most mathematically rigorous, complete, and efficient one. Ensure it satisfies all problem constraints.",
            contexts=results
        )

        # Step 5: Verify and finalize the solution
        verified_solution = await self.revise(
            instruction="Critique and refine the solution to ensure it is mathematically sound, adheres to all constraints, and handles edge cases. Provide detailed reasoning for each step.",
            context=best_solution
        )

        # Step 6: Summarize the final solution
        final_answer = await self.summarize(
            instruction="Condense the verified solution into a concise, polished form suitable for submission. Include the final answer prominently.",
            context=verified_solution
        )

        return final_answer