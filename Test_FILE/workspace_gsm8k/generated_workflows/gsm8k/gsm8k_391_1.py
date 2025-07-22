# Workflow ID: gsm8k_391_1
# Benchmark: gsm8k
# Data Indices: [191, 714]

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
        This is a diverse and effective workflow using two distinct patterns:
        1. Parallel Ensemble (Fan-out/Fan-in) to generate multiple independent solutions
        2. Reflect and Regenerate to refine the best solution based on meta-cognitive critique
        
        Unlike the existing workflow which uses a single initial solution followed by reflection,
        this approach first explores multiple reasoning paths in parallel, then applies deep reflection
        to improve only the top-performing candidate — mimicking how humans solve complex problems:
        brainstorm many ideas → evaluate → focus on refining the best one.
        """
        # Step 1: Generate 3 different solutions via parallel ensemble (each with a unique strategy)
        solutions = []
        strategies = [
            "Break the problem into subproblems, solve each step-by-step.",
            "Use algebraic modeling: define variables, set up equations, solve systematically.",
            "Estimate first, then verify accuracy through reverse calculation."
        ]
        
        for i, strategy in enumerate(strategies):
            solution = await self.flexible_custom(
                custom_instruction=f"Apply this reasoning strategy: {strategy}",
                reasoning_pattern="sequential",
                steps=["analyze", "plan", "solve", "verify"]
            )
            solutions.append(solution)

        # Step 2: Use ScEnsemble to pick the most accurate solution from the three
        best_solution = await self.sc_ensemble(solutions=solutions)

        # Step 3: Critically reflect on the best solution — identify hidden assumptions, gaps, or alternative interpretations
        reflection = await self.reflect(pre_solution=best_solution)

        # Step 4: Use the reflection to guide a final regeneration of the solution
        final_solution = await self.custom(
            instruction=f"Given the following best solution:\n{best_solution}\n\n"
                       f"And this critical reflection:\n{reflection}\n\n"
                       "Now, provide a fully revised, logically robust, and clear solution that addresses all concerns raised in the reflection."
        )

        return final_solution