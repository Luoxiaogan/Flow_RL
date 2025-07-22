# Workflow ID: gsm8k_394_1
# Benchmark: gsm8k
# Data Indices: [834, 527, 32]

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
        1. Parallel Ensemble (Fan-out/Fan-in): Generate 3 independent solutions using different reasoning strategies.
        2. Reflect and Regenerate: Critically reflect on the best solution from the ensemble, then regenerate a final improved version based on that reflection.
        
        This structure introduces both parallel exploration and meta-cognitive refinement — fundamentally different from the existing single-path sequential + reflect approach.
        """
        # Step 1: Generate multiple candidate solutions in parallel using FlexibleCustom with different reasoning patterns
        solution_candidates = []
        for i in range(3):
            pattern = ["sequential", "iterative", "branching"][i]
            solution = await self.flexible_custom(
                custom_instruction="Solve the problem by applying a systematic method.",
                reasoning_pattern=pattern,
                steps=["analyze", "plan", "solve", "verify"],
                use_structured_output=True
            )
            solution_candidates.append(solution)

        # Step 2: Use ScEnsemble to select the best among the three candidates
        best_candidate = await self.sc_ensemble(solutions=solution_candidates)

        # Step 3: Reflect critically on the best candidate without rewriting it
        reflection = await self.reflect(pre_solution=best_candidate)

        # Step 4: Use the reflection to guide a new, refined solution via Custom instruction
        final_solution = await self.custom(
            instruction=f"Based on the following reflection about the best solution: {reflection}. "
                        f"Provide a fully revised, more accurate, and clearly explained answer that addresses the identified weaknesses."
        )

        return final_solution