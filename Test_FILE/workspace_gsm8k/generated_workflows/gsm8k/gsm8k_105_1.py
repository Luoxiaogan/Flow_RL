# Workflow ID: gsm8k_105_1
# Benchmark: gsm8k
# Data Indices: [264, 107]

class Workflow:
    def __init__(
        self,
        config,
        problem
    ) -> None:
        self.problem = problem
        self.config = create(config)
        self.custom = operator.Custom(self.config, self.problem)
        self.sc_ensemble = operator.ScEnsemble(self.config, self.problem)
        self.review = operator.Review(self.config, self.problem)
        self.reflect = operator.Reflect(self.config, self.problem)
        self.flexible_custom = operator.FlexibleCustom(self.config, self.problem)

    async def run_workflow(self):
        """
        This is a diverse and robust workflow using the Reflect-and-Regenerate pattern with Parallel Ensemble.
        It generates 3 solutions via varied instructions, then uses Reflect to critique each one before ensembling.
        This approach ensures both diversity in initial reasoning and meta-cognitive refinement.
        """

        # Step 1: Generate 3 independent solutions using different reasoning styles
        solution_list = []
        instructions = [
            "Solve by first identifying all known quantities and unknowns explicitly.",
            "Use a visual diagram or model to represent relationships in the problem.",
            "Start by writing out the full equation based on the text description."
        ]
        
        for instr in instructions:
            solution = await self.custom(instruction=instr)
            solution_list.append(solution)

        # Step 2: Use Reflect to generate critical feedback for each solution
        reflections = []
        for sol in solution_list:
            reflection = await self.reflect(pre_solution=sol)
            reflections.append(reflection)

        # Step 3: Create a new set of refined solutions based on reflections
        refined_solutions = []
        for i, sol in enumerate(solution_list):
            instruction = f"Based on the following reflection: '{reflections[i]}', improve the solution below:\n{sol}"
            improved = await self.custom(instruction=instruction)
            refined_solutions.append(improved)

        # Step 4: Use ScEnsemble to pick the most consistent and accurate solution from refined set
        best_solution = await self.sc_ensemble(solutions=refined_solutions)

        # Step 5: Final Review to polish clarity and correctness
        final_answer = await self.review(pre_solution=best_solution)

        return final_answer