# Workflow ID: gsm8k_292_1
# Benchmark: gsm8k
# Data Indices: [263, 143]

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
        Diverse and complex workflow using the Reflect-and-Regenerate pattern as the core logic.
        This is fundamentally different from the existing workflow because it centers on a single reflective loop rather than parallel ensembling or iterative refinement with structured steps.

        Key differences:
        - No parallel ensemble; instead, one initial solution → reflection → regeneration.
        - Uses only one major loop (reflect + regenerate) rather than multiple independent solution attempts.
        - Leverages `Reflect` to guide a new `Custom` call — not a FlexibleCustom iteration — making the logic more meta-cognitive and less procedural.
        - Avoids ScEnsemble entirely — no selection from multiple candidates.
        - Focuses on deep reasoning through critique, not brute-force diversity of approaches.

        This ensures logical novelty: it’s not about generating many solutions and choosing one, but about deeply understanding one solution and improving it through reflection.
        """
        # --- STEP 1: Generate Initial Solution ---
        initial_solution = await self.custom(
            instruction="Solve the problem step-by-step. Be clear, methodical, and show all calculations."
        )

        # --- STEP 2: Critically Reflect on the Solution ---
        reflection = await self.reflect(pre_solution=initial_solution)

        # --- STEP 3: Regenerate Using Reflection as Guidance ---
        final_answer = await self.custom(
            instruction=f"Given the following reflection on the previous attempt: '{reflection}'. "
                        "Now, solve the problem again, focusing on addressing the identified weaknesses or gaps. "
                        "Ensure your reasoning is logically sound, complete, and free of assumptions."
        )

        return final_answer