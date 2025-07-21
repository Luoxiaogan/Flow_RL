# Workflow ID: gsm8k_110_0
# Benchmark: gsm8k
# Data Indices: [364, 307, 739]

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
        This is a diverse and robust workflow using the Parallel Ensemble pattern.
        Generates 3 different solutions via varied reasoning approaches, then selects the best one.
        Final review ensures clarity and correctness.
        """
        # Step 1: Generate multiple solutions using different reasoning strategies
        solutions = []
        for i in range(3):
            if i == 0:
                # Strategy 1: Step-by-step breakdown with clear arithmetic logic
                instruction = "Solve the problem by breaking it into explicit steps: identify known quantities, perform operations sequentially, and verify each step."
            elif i == 1:
                # Strategy 2: Use structured formulaic approach
                instruction = "Represent the problem as a mathematical expression or equation. Define variables, set up the relationships, and compute the result."
            else:
                # Strategy 3: Apply flexible custom with iterative refinement
                flexible_solver = operator.FlexibleCustom(
                    self.config,
                    self.problem,
                    reasoning_pattern="iterative",
                    steps=["analyze", "compute", "verify"],
                    max_iterations=2
                )
                solution = await flexible_solver(custom_instruction="Apply iterative reasoning to solve the problem.")
                solutions.append(solution)
                continue  # Skip appending here since we already have it

            solution = await self.custom(instruction=instruction)
            solutions.append(solution)

        # Step 2: Use ScEnsemble to select the most consistent and accurate solution
        final_solution = await self.sc_ensemble(solutions=solutions)

        # Step 3: Final review to improve clarity and catch any remaining issues
        refined_solution = await self.review(pre_solution=final_solution)

        return refined_solution