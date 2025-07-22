# Workflow ID: gsm8k_315_1
# Benchmark: gsm8k
# Data Indices: [197, 994]

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
        Diverse and robust workflow using Parallel Ensemble with Structured Reasoning via FlexibleCustom.
        1. Generate 3 solutions using different reasoning patterns (sequential, iterative, branching) via FlexibleCustom — each with unique step structures.
        2. Use ScEnsemble to select the most consistent solution from these varied approaches.
        3. Perform a final review to polish clarity and correctness — ensuring the output is both accurate and well-explained.
        
        This structure leverages diversity in *how* reasoning is structured (not just what is reasoned), making it more resilient to blind spots in any single approach.
        """
        # --- Step 1: Generate 3 diverse solutions using FlexibleCustom with different reasoning patterns ---
        solutions = []
        
        # Sequential: Linear breakdown of knowns, unknowns, formulas, calculation
        seq_solution = await self.flexible_custom(
            custom_instruction="Solve this math problem by following a structured sequence: identify knowns, define unknowns, apply relevant formulas, then compute.",
            reasoning_pattern="sequential",
            steps=["identify_knowns", "identify_unknowns", "apply_formula", "calculate"]
        )
        solutions.append(seq_solution)

        # Iterative: Start with an estimate, refine through multiple passes
        iter_solution = await self.flexible_custom(
            custom_instruction="Begin with a rough estimate, then improve accuracy through iterative refinement.",
            reasoning_pattern="iterative",
            steps=["initial_estimate", "refine", "verify"],
            max_iterations=2
        )
        solutions.append(iter_solution)

        # Branching: Explore multiple paths (e.g., alternative interpretations or methods) before choosing one
        branch_solution = await self.flexible_custom(
            custom_instruction="Explore multiple possible strategies for solving this problem; choose the best path based on internal consistency.",
            reasoning_pattern="branching",
            steps=["consider_approach_a", "consider_approach_b", "select_best", "execute"]
        )
        solutions.append(branch_solution)

        # --- Step 2: Select the best solution using ScEnsemble ---
        best_solution = await self.sc_ensemble(solutions=solutions)

        # --- Step 3: Final Review for Clarity and Rigor ---
        final_answer = await self.review(pre_solution=best_solution)

        return final_answer