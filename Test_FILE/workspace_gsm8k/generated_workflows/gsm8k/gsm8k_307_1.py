# Workflow ID: gsm8k_307_1
# Benchmark: gsm8k
# Data Indices: [962, 532, 192]

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
        This is a diverse, multi-pattern workflow based on the Reflect and Regenerate pattern as the core logic.
        It uses:
        1. A single initial solution via Custom
        2. Critical reflection using the new 'Reflect' operator
        3. A targeted regeneration step that uses the reflection to guide a new solution
        4. Final polishing via FlexibleCustom in 'sequential' mode for structured clarity
        
        Key difference from existing: Instead of ensemble + iterative refinement, this focuses on deep meta-cognition — 
        generating one solution, reflecting on it critically, then rebuilding with that insight. No parallelism or multiple passes.
        """

        # Step 1: Generate an initial solution using standard reasoning
        initial_solution = await self.custom(
            instruction="Solve the problem step-by-step, explaining your reasoning clearly."
        )

        # Step 2: Critically reflect on the solution — identify assumptions, gaps, or logical weaknesses
        reflection = await self.reflect(pre_solution=initial_solution)

        # Step 3: Use the reflection to generate a superior, more robust solution
        improved_solution = await self.custom(
            instruction=f"Based on the following reflection: '{reflection}', "
                        "reconstruct the solution from scratch. Address all identified issues explicitly."
        )

        # Step 4: Final refinement using FlexibleCustom in sequential mode for clarity and structure
        final_answer = await self.flexible_custom(
            custom_instruction="Break down the solution into clear stages: analyze, plan, solve, verify.",
            reasoning_pattern="sequential",
            steps=["analyze", "plan", "solve", "verify"],
            use_structured_output=True
        )

        return final_answer