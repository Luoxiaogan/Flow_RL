# Workflow ID: gsm8k_389_1
# Benchmark: gsm8k
# Data Indices: [417, 303, 361]

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
        This is a diverse and robust workflow using the Reflect-and-Regenerate pattern with Parallel Ensemble.
        Step 1: Generate multiple solutions via FlexibleCustom in parallel (different reasoning patterns).
        Step 2: Use Reflect to critique each solution independently — not just fix, but analyze potential flaws.
        Step 3: Regenerate improved versions based on reflections.
        Step 4: Ensembles final candidates for consensus.
        Step 5: Final review for clarity and correctness.
        
        Key differences from existing:
        - Uses Reflect *before* ensembling (not after), enabling meta-cognitive feedback.
        - Leverages FlexibleCustom with distinct reasoning patterns per solution (parallel + branching logic).
        - Does NOT do single-pass generation → ensemble → review; instead, it iteratively improves based on reflection.
        """
        # --- STEP 1: Generate 3 diverse solutions using different FlexibleCustom strategies ---
        solution_list = []
        configs = [
            {"reasoning_pattern": "sequential", "steps": ["identify_knowns", "set_up_equations", "solve"]},
            {"reasoning_pattern": "iterative", "steps": ["initial_guess", "refine", "verify"], "max_iterations": 2},
            {"reasoning_pattern": "branching", "steps": ["analyze_case_a", "analyze_case_b", "combine"]}
        ]
        
        for i, cfg in enumerate(configs):
            solution = await self.flexible_custom(
                custom_instruction="Solve this math problem using a structured reasoning approach.",
                previous_results=None,
                **cfg
            )
            solution_list.append(solution)

        # --- STEP 2: Reflect on each solution independently to uncover hidden assumptions or errors ---
        reflections = []
        for sol in solution_list:
            reflection = await self.reflect(pre_solution=sol)
            reflections.append(reflection)

        # --- STEP 3: Regenerate improved solutions based on reflections ---
        improved_solutions = []
        for i, sol in enumerate(solution_list):
            instruction = f"Based on the following reflection about your earlier attempt: '{reflections[i]}'. Now, provide a revised solution that addresses these points."
            new_sol = await self.custom(instruction=instruction)
            improved_solutions.append(new_sol)

        # --- STEP 4: Use ScEnsemble to pick the most consistent and accurate answer ---
        best_solution = await self.sc_ensemble(solutions=improved_solutions)

        # --- STEP 5: Final refinement with Review for clarity, completeness, and logical flow ---
        final_answer = await self.review(pre_solution=best_solution)

        return final_answer