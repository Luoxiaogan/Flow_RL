# Workflow ID: gsm8k_94_1
# Benchmark: gsm8k
# Data Indices: [706, 167]

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
        Diverse and robust workflow using Parallel Ensemble with varied strategies.
        Step 1: Generate 3 solutions using different reasoning patterns via FlexibleCustom.
        Step 2: Use ScEnsemble to select the most consistent solution.
        Step 3: Final review for clarity and correctness — no reflection needed here since ensemble already filters out weak logic.
        
        This differs from the existing workflow by:
        - Using FlexibleCustom with distinct reasoning patterns (sequential, iterative, branching) instead of identical custom prompts
        - Avoiding reflection/regeneration loop — relies on diversity in initial generation rather than meta-cognition
        - Simpler control flow: fan-out → ensemble → final polish
        """
        # --- PARALLEL ENSEMBLE WITH DIVERSE STRATEGIES ---
        solutions = []

        # Strategy 1: Sequential decomposition (step-by-step breakdown)
        sequential_solution = await self.flexible_custom(
            custom_instruction="Break down the problem into clear logical steps.",
            reasoning_pattern="sequential",
            steps=["understand", "analyze", "solve", "verify"]
        )
        solutions.append(sequential_solution)

        # Strategy 2: Iterative refinement (start rough, improve over passes)
        iterative_solution = await self.flexible_custom(
            custom_instruction="Start with an approximate answer, then refine it through multiple passes.",
            reasoning_pattern="iterative",
            steps=["initial_guess", "refine", "validate"],
            max_iterations=2
        )
        solutions.append(iterative_solution)

        # Strategy 3: Branching approach (consider alternative interpretations)
        branching_solution = await self.flexible_custom(
            custom_instruction="Explore multiple possible interpretations or paths to solve this problem.",
            reasoning_pattern="branching",
            steps=["identify_possibilities", "evaluate_options", "choose_best"]
        )
        solutions.append(branching_solution)

        # --- SELECT BEST SOLUTION VIA SCENSEMBLE ---
        best_solution = await self.sc_ensemble(solutions=solutions)

        # --- FINAL REVIEW FOR CLARITY AND CORRECTNESS ---
        final_answer = await self.review(pre_solution=best_solution)

        return final_answer