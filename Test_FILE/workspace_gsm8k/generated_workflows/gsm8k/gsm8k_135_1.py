# Workflow ID: gsm8k_135_1
# Benchmark: gsm8k
# Data Indices: [779, 570, 772]

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
        Novel workflow combining: 
        1. Iterative Refinement (via FlexibleCustom in iterative mode) 
        2. Conditional Branching based on reflection content
        3. Parallel Ensemble as a fallback when initial refinement stalls
        
        This differs from the existing logic by starting with structured iterative improvement rather than parallel generation, and using branching logic to decide whether to continue refining or fall back to ensemble.
        """

        # --- Step 1: Initial Solution via Iterative Refinement (Pattern 1) ---
        initial_solution = await self.flexible_custom(
            custom_instruction="Begin solving the problem using a step-by-step approach.",
            reasoning_pattern="iterative",
            steps=["understand", "plan", "solve", "verify"],
            max_iterations=2,
            use_structured_output=True
        )

        # --- Step 2: Reflect on the Result ---
        reflection = await self.reflect(pre_solution=initial_solution)

        # --- Step 3: Conditional Logic Based on Reflection ---
        if "assumption" in reflection.lower() or "unclear" in reflection.lower():
            # If assumptions are flagged, try another round of iterative refinement with improved instructions
            refined_solution = await self.flexible_custom(
                custom_instruction="Refine the solution by addressing these issues: " + reflection,
                reasoning_pattern="iterative",
                steps=["analyze_assumptions", "correct_errors", "revalidate"],
                max_iterations=3,
                use_structured_output=True
            )
        elif "no major flaws" in reflection.lower():
            # If no issues found, return the original solution
            refined_solution = initial_solution
        else:
            # Otherwise, fallback to Parallel Ensemble for robustness
            candidate_solutions = []
            for i in range(4):  # Generate more candidates due to uncertainty
                candidate = await self.custom(instruction="Solve the problem independently using a different method.")
                candidate_solutions.append(candidate)
            
            refined_solution = await self.sc_ensemble(solutions=candidate_solutions)

        # --- Step 4: Final Review for polish ---
        final_answer = await self.review(pre_solution=refined_solution)

        return final_answer