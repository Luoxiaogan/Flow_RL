# Workflow ID: gsm8k_154_1
# Benchmark: gsm8k
# Data Indices: [314, 976, 512]

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
        This is a diverse and complex workflow that implements the 'Reflect and Regenerate' pattern as the core logic.
        It uses a novel structure: generate → reflect → regenerate (with no ensemble or iterative refinement).
        This avoids the parallel fan-out and instead focuses on deep meta-cognition — critical reflection leading to a superior solution.
        """

        # Step 1: Generate an initial solution using Custom with clear reasoning instruction
        initial_solution = await self.custom(
            instruction="Solve the problem step-by-step. Break it down into smaller parts and explain each step clearly."
        )

        # Step 2: Critically reflect on the solution without rewriting it — identify assumptions, gaps, or potential errors
        reflection = await self.reflect(pre_solution=initial_solution)

        # Step 3: Use the reflection to guide a new, improved solution via FlexibleCustom in sequential mode
        # This ensures structured reasoning based on critique — not just reworking but rebuilding with insight
        final_solution = await self.flexible_custom(
            custom_instruction=f"Based on the following reflection: {reflection}. Now, solve the problem again using a structured, step-by-step approach that addresses all identified issues.",
            reasoning_pattern="sequential",
            steps=["analyze", "plan", "solve", "verify"]
        )

        return final_solution