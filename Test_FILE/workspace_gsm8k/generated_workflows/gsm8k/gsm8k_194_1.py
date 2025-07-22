# Workflow ID: gsm8k_194_1
# Benchmark: gsm8k
# Data Indices: [37, 331, 933]

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
        This is a diverse and efficient workflow using Iterative Refinement with FlexibleCustom.
        Step 1: Use FlexibleCustom in iterative mode to generate an initial solution, then refine it over 2 passes.
        Step 2: If the final refined solution seems incomplete or ambiguous, use Reflect to critique it and generate a final answer based on that reflection.
        This approach combines structured iteration with meta-cognitive reflection — different from the existing parallel+reflect strategy.
        """
        # --- Phase 1: Iterative Refinement using FlexibleCustom ---
        iterative_solver = self.flexible_custom(
            reasoning_pattern="iterative",
            steps=["analyze", "solve", "verify"],
            max_iterations=2,
            custom_instruction="Solve this math problem by breaking it into logical sub-problems and verifying each step."
        )
        intermediate_solution = await iterative_solver

        # --- Phase 2: Optional Reflection for Final Quality Check ---
        reflection = await self.reflect(pre_solution=intermediate_solution)
        
        # If the reflection indicates potential issues (e.g., mentions ambiguity, missing assumptions),
        # we regenerate with guidance. Otherwise, return the intermediate solution directly.
        if "error" in reflection.lower() or "missing" in reflection.lower() or "assumption" in reflection.lower():
            final_instruction = (
                "Based on the following reflection, improve the previous solution:\n\n"
                f"{reflection}\n\n"
                "Provide a clear, precise, and complete answer addressing all identified concerns."
            )
            final_answer = await self.custom(instruction=final_instruction)
        else:
            final_answer = intermediate_solution

        return final_answer