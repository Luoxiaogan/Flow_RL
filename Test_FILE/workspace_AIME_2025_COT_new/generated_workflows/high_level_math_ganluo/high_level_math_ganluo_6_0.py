# Workflow ID: high_level_math_ganluo_6_0
# Benchmark: high_level_math_ganluo
# Data Indices: [15]

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

        # Step 1: Extract key information and structure the problem
        extraction = await self.generate(
            instruction="Extract all numerical values, relationships, and constraints from the problem. "
                        "Organize them into a structured format, clearly identifying knowns and unknowns. "
                        "Include any implicit assumptions or geometric properties that might be relevant.",
            context=self.problem_text
        )

        # Step 2: Generate multiple solution paths in parallel
        soln_path_1 = self.generate(
            instruction=f"Using coordinate geometry, place the points on a straight line and calculate the area of triangle BGE. "
                        f"Use the extracted information: {extraction}. "
                        f"Clearly show all calculations and reasoning steps.",
            context=self.problem_text
        )
        soln_path_2 = self.generate(
            instruction=f"Using synthetic geometry, analyze the relationships between the points and distances. "
                        f"Apply geometric theorems to find the area of triangle BGE. "
                        f"Use the extracted information: {extraction}. "
                        f"Clearly show all reasoning steps.",
            context=self.problem_text
        )
        soln_path_3 = self.generate(
            instruction=f"Using trigonometric methods, calculate the angles and side lengths of triangle BGE. "
                        f"Use the extracted information: {extraction}. "
                        f"Clearly show all calculations and reasoning steps.",
            context=self.problem_text
        )
        solutions = await asyncio.gather(soln_path_1, soln_path_2, soln_path_3)

        # Step 3: Revise and validate each solution
        revised_solutions = await asyncio.gather(
            self.revise(
                instruction="Critique this solution for accuracy, completeness, and adherence to the problem constraints. "
                            "Refine any ambiguous or incorrect steps. Ensure the final result is mathematically sound.",
                context=solutions[0]
            ),
            self.revise(
                instruction="Critique this solution for accuracy, completeness, and adherence to the problem constraints. "
                            "Refine any ambiguous or incorrect steps. Ensure the final result is mathematically sound.",
                context=solutions[1]
            ),
            self.revise(
                instruction="Critique this solution for accuracy, completeness, and adherence to the problem constraints. "
                            "Refine any ambiguous or incorrect steps. Ensure the final result is mathematically sound.",
                context=solutions[2]
            )
        )

        # Step 4: Ensemble decision to select the best solution
        final_solution = await self.ensemble(
            instruction="Compare the three revised solutions. Evaluate their correctness, clarity, and elegance. "
                        "Select the most accurate and well-reasoned solution. Resolve any discrepancies between the solutions.",
            contexts=revised_solutions
        )

        # Step 5: Summarize the final answer
        final_answer = await self.summarize(
            instruction="Extract the final answer from the selected solution. "
                        "Ensure it is presented in a clear and concise format, with appropriate units if applicable.",
            context=final_solution
        )

        return final_answer