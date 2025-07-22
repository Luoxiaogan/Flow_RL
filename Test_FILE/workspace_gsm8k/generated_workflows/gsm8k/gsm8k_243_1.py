# Workflow ID: gsm8k_243_1
# Benchmark: gsm8k
# Data Indices: [359, 158]

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
        This is a diverse workflow using the Parallel Ensemble pattern for robustness.
        Step 1: Generate 3 independent solutions using varied reasoning strategies via FlexibleCustom.
        Step 2: Use ScEnsemble to select the most consistent and accurate solution from the three.
        Step 3: Final review to ensure clarity and completeness — this step adds a layer of quality control after ensemble selection.
        """
        # Generate multiple candidate solutions using different structured approaches
        solutions = []
        for i in range(3):
            if i == 0:
                # Strategy 1: Focus on logical breakdown with clear steps
                sol = await self.flexible_custom(
                    custom_instruction="Break down the problem into explicit steps and solve each systematically.",
                    reasoning_pattern="sequential",
                    steps=["understand", "analyze", "formulate", "solve"]
                )
            elif i == 1:
                # Strategy 2: Use iterative refinement internally (flexible_custom handles this)
                sol = await self.flexible_custom(
                    custom_instruction="Start with an initial estimate, then refine through multiple iterations.",
                    reasoning_pattern="iterative",
                    steps=["initial_guess", "refine", "validate"],
                    max_iterations=2
                )
            else:
                # Strategy 3: Branch based on possible interpretations (e.g., assumptions, edge cases)
                sol = await self.flexible_custom(
                    custom_instruction="Consider alternative interpretations of the problem and resolve conflicts.",
                    reasoning_pattern="branching",
                    steps=["identify_assumptions", "explore_options", "resolve_conflicts", "conclude"]
                )
            solutions.append(sol)

        # Select the best solution using ensemble logic — promotes robustness by consensus
        best_solution = await self.sc_ensemble(solutions=solutions)

        # Final review to polish clarity, fix minor errors, and ensure completeness
        final_answer = await self.review(pre_solution=best_solution)

        return final_answer