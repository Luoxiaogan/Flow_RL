# Workflow ID: gsm8k_11_1
# Benchmark: gsm8k
# Data Indices: [771, 954]

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
        Diverse and complex workflow combining Iterative Refinement + Reflect-and-Regenerate with conditional branching.
        Step 1: Use FlexibleCustom in iterative mode to generate an initial solution with structured reasoning.
        Step 2: Review the result to improve clarity and correctness.
        Step 3: Reflect on the reviewed solution — if it contains logical gaps or assumptions, regenerate using a new strategy (branching logic).
        Step 4: If no major flaws are found, return the solution; otherwise, use a parallel ensemble of two different approaches guided by the reflection.
        """

        # --- STEP 1: Initial Solution via Iterative Reasoning ---
        initial_solution = await self.flexible_custom(
            custom_instruction="Solve the problem using an iterative approach: analyze, plan, solve, verify.",
            reasoning_pattern="iterative",
            steps=["analyze", "plan", "solve", "verify"],
            max_iterations=2
        )

        # --- STEP 2: Improve with Review ---
        improved_solution = await self.review(pre_solution=initial_solution)

        # --- STEP 3: Reflect to Identify Critical Flaws ---
        reflection = await self.reflect(pre_solution=improved_solution)

        # --- STEP 4: Conditional Logic Based on Reflection ---
        if "assumption" in reflection.lower() or "gap" in reflection.lower() or "unclear" in reflection.lower():
            # If critical issues exist → Generate two alternative solutions and ensemble
            candidate_solutions = []
            for _ in range(2):
                alt_solution = await self.custom(
                    instruction="Solve the problem from scratch using a completely different method than before. Focus on verifying each step."
                )
                candidate_solutions.append(alt_solution)

            final_answer = await self.sc_ensemble(solutions=candidate_solutions)
        else:
            # No major flaws → Return improved solution as is
            final_answer = improved_solution

        return final_answer