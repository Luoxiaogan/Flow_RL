# Workflow ID: gsm8k_80_1
# Benchmark: gsm8k
# Data Indices: [225, 238]

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
        This is a diverse and reflective workflow using the 'Iterative Refinement with Parallel Exploration' pattern.
        It begins with an initial solution, then explores multiple alternative approaches in parallel (via FlexibleCustom),
        uses reflection to guide refinement of each, and finally selects the best solution via ScEnsemble.
        This differs from the existing workflow by introducing parallel reasoning paths and structured iterative improvement.
        """

        # Step 1: Generate an initial solution using basic reasoning
        initial_solution = await self.custom(
            instruction="Solve the problem step-by-step, explaining your reasoning clearly."
        )

        # Step 2: Use Reflect to critically assess the initial solution — identify hidden assumptions or oversights
        reflection = await self.reflect(pre_solution=initial_solution)

        # Step 3: Create multiple alternative solutions using FlexibleCustom in "parallel" mode
        # This explores different reasoning strategies (e.g., algebraic, tabular, estimation-based) simultaneously
        parallel_solutions = []
        for i in range(3):  # Try 3 different approaches
            if i == 0:
                instruction = f"Use an algebraic approach based on the reflection: {reflection}"
            elif i == 1:
                instruction = f"Use a step-by-step numerical method informed by: {reflection}"
            else:
                instruction = f"Use a simplified estimation strategy guided by: {reflection}"

            solution = await self.flexible_custom(
                custom_instruction=instruction,
                reasoning_pattern="sequential",
                steps=["analyze", "model", "compute", "verify"]
            )
            parallel_solutions.append(solution)

        # Step 4: Evaluate all parallel solutions using ScEnsemble to pick the most accurate one
        final_solution = await self.sc_ensemble(solutions=parallel_solutions)

        return final_solution