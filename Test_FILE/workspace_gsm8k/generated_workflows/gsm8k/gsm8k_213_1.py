# Workflow ID: gsm8k_213_1
# Benchmark: gsm8k
# Data Indices: [846, 876, 857]

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
        This is a diverse workflow using two distinct patterns:
        1. Parallel Ensemble (Fan-out/Fan-in): Generate 3 different solutions via Custom with varied instructions.
        2. Reflect and Regenerate: Critically reflect on the best solution from the ensemble, then regenerate a refined version.
        
        This structure ensures robustness through diversity of initial approaches and meta-cognition for refinement — fundamentally different from the existing single-pass 'Reflect and Regenerate' logic.
        """

        # Step 1: Generate multiple independent solutions in parallel (fan-out)
        solution1 = await self.custom(instruction="Solve the problem by first identifying all known quantities and unknowns.")
        solution2 = await self.custom(instruction="Break the problem into smaller sub-problems and solve each step-by-step.")
        solution3 = await self.custom(instruction="Use dimensional analysis or unit-based reasoning to ensure consistency across steps.")

        # Step 2: Evaluate and select the best solution using ScEnsemble (fan-in)
        solutions = [solution1, solution2, solution3]
        best_solution = await self.sc_ensemble(solutions=solutions)

        # Step 3: Critically reflect on the best solution — identify potential flaws, assumptions, or alternative interpretations
        reflection = await self.reflect(pre_solution=best_solution)

        # Step 4: Use reflection to guide a new, improved solution via FlexibleCustom with iterative reasoning pattern
        # This introduces a structured, multi-stage refinement process not present in the original
        improved_solution = await self.flexible_custom(
            custom_instruction="Based on the reflection provided, refine the solution with explicit validation of assumptions and logical flow.",
            reasoning_pattern="iterative",
            steps=["analyze_reflection", "validate_assumptions", "reconstruct_reasoning", "verify_final_answer"],
            max_iterations=2
        )

        return improved_solution