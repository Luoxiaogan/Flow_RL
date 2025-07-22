# Workflow ID: gsm8k_71_1
# Benchmark: gsm8k
# Data Indices: [322, 173, 738]

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
        This is a diverse and complex workflow combining:
        1. Iterative Refinement (with Review) to improve an initial solution
        2. Conditional Branching based on reflection content to choose between two strategies
        
        Step 1: Generate an initial solution using FlexibleCustom in sequential mode.
        Step 2: Refine it iteratively using Review until no further improvement is detected or max iterations reached.
        Step 3: Reflect on the final refined solution — if reflection suggests missing logic, use branching to try a different reasoning path.
        Step 4: If branching is triggered, generate a new solution using a parallel ensemble of two distinct strategies.
        Step 5: Final selection via ScEnsemble from both the refined path and the branched solutions.
        """

        # --- STEP 1: Initial Solution via Sequential Reasoning ---
        initial_solution = await self.flexible_custom(
            custom_instruction="Solve this math problem step-by-step by identifying knowns, unknowns, applying relevant formulas, and verifying each step.",
            reasoning_pattern="sequential",
            steps=["identify_knowns", "identify_unknowns", "apply_formula", "calculate", "verify"]
        )

        # --- STEP 2: Iterative Refinement using Review ---
        current_solution = initial_solution
        for iteration in range(2):  # Max 2 refinement passes
            improved_solution = await self.review(pre_solution=current_solution)
            # If no meaningful change, stop early
            if improved_solution == current_solution:
                break
            current_solution = improved_solution

        # --- STEP 3: Reflect on the refined solution to detect potential flaws ---
        reflection_text = await self.reflect(pre_solution=current_solution)

        # --- STEP 4: Conditional Logic Based on Reflection ---
        # If reflection indicates possible error or ambiguity, branch into parallel strategies
        if "error" in reflection_text.lower() or "ambiguous" in reflection_text.lower() or "missing" in reflection_text.lower():
            # Generate two alternative approaches in parallel
            solution_a = await self.custom(instruction="Solve using algebraic equations and clear variable definitions.")
            solution_b = await self.custom(instruction="Solve using unit-based reasoning: break everything down into units and track them through each step.")

            # Combine with original refined solution for ensemble
            all_solutions = [current_solution, solution_a, solution_b]
            final_solution = await self.sc_ensemble(solutions=all_solutions)
        else:
            # No branching needed — return the refined solution
            final_solution = current_solution

        return final_solution