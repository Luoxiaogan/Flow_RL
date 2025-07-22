# Workflow ID: gsm8k_354_1
# Benchmark: gsm8k
# Data Indices: [987, 445]

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
        Diverse and effective workflow combining Iterative Refinement + Branching Logic.
        
        1. Use FlexibleCustom in 'iterative' mode to generate an initial solution with structured steps.
        2. If the reflection indicates uncertainty or multiple interpretations, branch into two parallel paths:
           - One for verification via Review
           - One for re-solving from scratch using a different reasoning pattern (sequential vs iterative).
        3. Combine both results via ScEnsemble to select the best final answer.
        
        This introduces conditional branching based on meta-cognition (reflection), making it fundamentally different from the existing linear flow.
        """
        # --- Step 1: Generate initial solution using iterative refinement pattern ---
        initial_solution = await self.flexible_custom(
            reasoning_pattern="iterative",
            steps=["understand", "plan", "compute", "verify"],
            max_iterations=2,
            custom_instruction="Solve the problem step-by-step with iterative improvement."
        )

        # --- Step 2: Reflect on the solution to detect ambiguity or risk ---
        reflection = await self.reflect(pre_solution=initial_solution)

        # --- Step 3: Conditional branching logic based on reflection ---
        if "ambiguous" in reflection.lower() or "multiple interpretations" in reflection.lower():
            # --- Branch A: Improve via review ---
            reviewed_solution = await self.review(pre_solution=initial_solution)

            # --- Branch B: Re-solve using sequential approach ---
            fresh_solution = await self.flexible_custom(
                reasoning_pattern="sequential",
                steps=["identify_knowns", "define_unknowns", "apply_formula", "calculate"],
                custom_instruction="Solve the problem using a strict, linear sequence of logical steps."
            )

            # --- Combine both branches using ensemble ---
            solutions = [reviewed_solution, fresh_solution]
            final_solution = await self.sc_ensemble(solutions=solutions)
        else:
            # --- No ambiguity detected — proceed with simple review ---
            final_solution = await self.review(pre_solution=initial_solution)

        return final_solution