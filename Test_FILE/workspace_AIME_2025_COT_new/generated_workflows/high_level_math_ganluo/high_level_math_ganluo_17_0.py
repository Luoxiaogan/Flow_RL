# Workflow ID: high_level_math_ganluo_17_0
# Benchmark: high_level_math_ganluo
# Data Indices: [13]

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

        # Step 1: Problem Decomposition and Understanding
        problem_analysis = await self.generate(
            instruction="Extract all key information from the problem, including given values, constraints, and the specific question being asked. Organize this information into categories such as numerical data, geometric relationships, and objectives.",
            context=self.problem_text
        )

        # Step 2: Generate Multiple Solution Approaches
        algebraic_approach = self.generate(
            instruction=f"Using the extracted information: {problem_analysis}, develop an algebraic solution path. Focus on equations, inequalities, and relationships between variables.",
            context=self.problem_text
        )
        geometric_approach = self.generate(
            instruction=f"Using the extracted information: {problem_analysis}, develop a geometric solution path. Consider coordinate geometry, synthetic geometry, and trigonometric relationships.",
            context=self.problem_text
        )
        combinatorial_approach = self.generate(
            instruction=f"Using the extracted information: {problem_analysis}, explore a combinatorial or probabilistic solution path if applicable. Focus on counting principles, recursive structures, or generating functions.",
            context=self.problem_text
        )

        # Execute approaches in parallel
        approaches = await asyncio.gather(algebraic_approach, geometric_approach, combinatorial_approach)

        # Step 3: Evaluate and Select the Best Approach
        best_approach = await self.ensemble(
            instruction="Compare the provided solution approaches based on correctness, simplicity, and adherence to the problem constraints. Select the most promising approach.",
            contexts=approaches
        )

        # Step 4: Refine the Chosen Solution
        refined_solution = await self.revise(
            instruction="Critique and improve the provided solution. Ensure mathematical rigor, clarity, and correctness. Verify that all constraints are satisfied.",
            context=best_approach
        )

        # Step 5: Summarize the Final Answer
        final_answer = await self.summarize(
            instruction="Condense the solution into a concise format. Include the final answer in the required form (e.g., m+n+p).",
            context=refined_solution
        )

        return final_answer