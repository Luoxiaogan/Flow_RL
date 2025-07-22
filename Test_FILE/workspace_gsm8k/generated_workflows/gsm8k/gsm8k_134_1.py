# Workflow ID: gsm8k_134_1
# Benchmark: gsm8k
# Data Indices: [728, 293, 378]

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
        This is a diverse and complex workflow using the Iterative Refinement pattern.
        1. Generate an initial solution with a clear, step-by-step instruction.
        2. Apply the Review operator twice to progressively improve it — each review builds on the previous one.
        3. After refinement, use Reflect to critique the final result for any hidden assumptions or edge cases.
        4. If reflection suggests improvement, generate a final polished version using FlexibleCustom in sequential mode to ensure structured reasoning.
        
        Key difference from existing: Uses pure iterative refinement (no parallelism or ensembling), focuses on progressive enhancement via Review, and ends with a reflective check — all within a single-threaded, logically deep path.
        """

        # --- STEP 1: Initial Solution ---
        initial_solution = await self.custom(
            instruction="Solve this math word problem step-by-step, explaining each logical step clearly and concisely."
        )

        # --- STEP 2: Iterative Refinement (Review x2) ---
        intermediate_solution = await self.review(pre_solution=initial_solution)
        final_refined_solution = await self.review(pre_solution=intermediate_solution)

        # --- STEP 3: Reflect on Final Refined Solution ---
        reflection = await self.reflect(pre_solution=final_refined_solution)

        # --- STEP 4: Conditional Final Polish Using FlexibleCustom (Sequential Mode) ---
        if "assumption" in reflection.lower() or "error" in reflection.lower():
            final_answer = await self.flexible_custom(
                custom_instruction="Re-solve the problem with careful attention to potential assumptions or logical gaps identified in the reflection.",
                previous_results=[final_refined_solution, reflection],
                reasoning_pattern="sequential",
                steps=["analyze_assumptions", "reconstruct_logic", "verify_final_answer"]
            )
        else:
            final_answer = final_refined_solution

        return final_answer