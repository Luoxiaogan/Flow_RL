# Workflow ID: gsm8k_48_0
# Benchmark: gsm8k
# Data Indices: [275, 373, 334]

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
        Diverse and complex workflow combining Parallel Ensemble + Reflect-and-Regenerate.
        Step 1: Generate multiple candidate solutions in parallel (Fan-out).
        Step 2: Select the best one using ScEnsemble (Fan-in).
        Step 3: Reflect on the selected solution to identify potential flaws or missed angles.
        Step 4: Use that reflection to guide a new, improved solution via FlexibleCustom with iterative refinement.
        """
        # --- STEP 1: Parallel Ensemble (Fan-out) ---
        solution_candidates = []
        for i in range(3):  # Generate 3 independent solutions
            candidate = await self.custom(
                instruction="Solve the problem by breaking it into logical steps. Be thorough and explain each step clearly."
            )
            solution_candidates.append(candidate)

        # --- STEP 2: Fan-in via ScEnsemble ---
        best_solution = await self.sc_ensemble(solutions=solution_candidates)

        # --- STEP 3: Reflect on the Best Solution ---
        reflection = await self.reflect(pre_solution=best_solution)

        # --- STEP 4: Regenerate Based on Reflection (Reflect-and-Regenerate Pattern) ---
        if "incomplete" in reflection.lower() or "assumption" in reflection.lower():
            final_solution = await self.flexible_custom(
                custom_instruction="Re-solve the problem incorporating the following reflection: " + reflection,
                reasoning_pattern="iterative",
                steps=["analyze", "rethink_assumptions", "recalculate", "verify"],
                max_iterations=2
            )
        else:
            # If no major flaw found, use a sequential approach for clarity
            final_solution = await self.flexible_custom(
                custom_instruction="Provide a clear, structured explanation of the solution based on the best candidate.",
                reasoning_pattern="sequential",
                steps=["identify_knowns", "set_up_equations", "solve", "validate"]
            )

        return final_solution