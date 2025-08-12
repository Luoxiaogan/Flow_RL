# Workflow ID: high_level_math_ganluo_0_0
# Benchmark: high_level_math_ganluo
# Data Indices: [6]

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
        Remember: 
        - Use detailed, comprehensive instructions
        - Dynamic instruction construction is powerful
        - All operators expect (instruction: str, context: str) except Ensemble which takes contexts: List[str]
        """
        import asyncio

        # Step 1: Problem Decomposition
        decomposition = await self.generate(
            instruction="Extract all key components of the problem, including numerical values, constraints, and relationships. "
                        "Identify the type of problem (e.g., combinatorics, number theory) and list any formulas or theorems that might apply.",
            context=self.problem_text
        )

        # Step 2: Solution Exploration (Parallel Execution)
        algebraic_solution = self.generate(
            instruction=f"Using the extracted components: {decomposition}, "
                        "solve the problem using algebraic methods. Include detailed reasoning and intermediate steps.",
            context=self.problem_text
        )
        combinatorial_solution = self.generate(
            instruction=f"Using the extracted components: {decomposition}, "
                        "solve the problem using combinatorial methods. Include detailed reasoning and intermediate steps.",
            context=self.problem_text
        )
        geometric_solution = self.generate(
            instruction=f"Using the extracted components: {decomposition}, "
                        "solve the problem using geometric methods if applicable. Include detailed reasoning and intermediate steps.",
            context=self.problem_text
        )
        solutions = await asyncio.gather(algebraic_solution, combinatorial_solution, geometric_solution)

        # Step 3: Refinement and Critique
        refined_solutions = []
        for solution in solutions:
            refined = await self.revise(
                instruction="Critique this solution for mathematical correctness, completeness, and adherence to problem constraints. "
                            "Suggest improvements if necessary.",
                context=solution
            )
            refined_solutions.append(refined)

        # Step 4: Comparison and Selection
        best_solution = await self.ensemble(
            instruction="Compare these solutions and select the most robust, correct, and elegant one. "
                        "If multiple solutions are valid, synthesize their insights into a unified approach.",
            contexts=refined_solutions
        )

        # Step 5: Final Verification and Summary
        final_answer = await self.summarize(
            instruction="Condense the final solution into a concise, clear format. Ensure it satisfies all problem constraints "
                        "and provide the answer in the required format (e.g., simplified fractions, boxed answers).",
            context=best_solution
        )

        return final_answer