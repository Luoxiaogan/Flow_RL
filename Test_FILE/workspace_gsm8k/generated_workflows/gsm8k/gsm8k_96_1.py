# Workflow ID: gsm8k_96_1
# Benchmark: gsm8k
# Data Indices: [623, 942]

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
        This is fundamentally different from the existing workflow because it uses a single initial solution,
        followed by deep reflection, and then leverages FlexibleCustom in a branching pattern to explore alternative reasoning paths based on that reflection — not just iterative refinement.

        Key differences:
        - No parallel ensemble (fan-out/fan-in) used at all.
        - Uses 'Reflect' to generate critical insights, which are then used to guide a *branching* strategy via FlexibleCustom.
        - The final step doesn't simply refine the same solution but explores multiple reasoning paths informed by reflection — this introduces structural diversity in control flow.
        """

        # --- STEP 1: Generate an initial solution ---
        initial_solution = await self.custom(
            instruction="Solve the problem step-by-step. Identify all given quantities and relationships. Be explicit about each calculation."
        )

        # --- STEP 2: Critically reflect on the solution without rewriting it ---
        reflection = await self.reflect(pre_solution=initial_solution)

        # --- STEP 3: Use reflection to guide a branching reasoning process ---
        # Here we use FlexibleCustom with a "branching" pattern to explore different interpretations or assumptions revealed in the reflection.
        # For example, if the reflection says "the problem might be interpreted differently depending on whether coupons apply per bottle or total", 
        # this allows us to test both cases systematically.
        #
        # This is a novel use of FlexibleCustom — not just for iteration, but for structured exploration of alternatives.
        branched_solution = await self.flexible_custom(
            custom_instruction=f"Based on the following reflection: '{reflection}'. Now solve the problem using a branching approach: consider alternative interpretations of the problem and evaluate each path.",
            reasoning_pattern="branching",
            steps=["identify_assumptions", "branch_interpretations", "evaluate_paths", "select_best"],
            use_structured_output=True
        )

        return branched_solution