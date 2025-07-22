# Workflow ID: gsm8k_7_1
# Benchmark: gsm8k
# Data Indices: [539, 39, 437]

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
        Diverse and robust workflow using a novel structure: 
        - Parallel Ensemble with 3 distinct reasoning strategies (different prompts)
        - Select best solution via ScEnsemble
        - Apply Reflect to critique it (meta-cognition)
        - Use FlexibleCustom in BRANCHING pattern to explore alternative paths based on reflection
        - Final Review for polish
        
        This differs from the existing logic by:
        1. Using BRANCHING reasoning instead of iterative refinement
        2. Introducing conditional exploration after reflection (not just one fixed path)
        3. Including a final Review step that wasn't in the original
        4. Not relying on a single "fix" but branching into multiple potential improvements
        """
        # --- STEP 1: Generate 3 diverse solutions using different strategies ---
        solutions = []
        strategies = [
            "Solve using dimensional analysis: track units at each step to avoid errors.",
            "Break the problem into subproblems: identify what must be calculated first, then second, etc.",
            "Use estimation first, then exact calculation: get a ballpark figure before computing precisely."
        ]
        
        for strategy in strategies:
            sol = await self.custom(instruction=strategy)
            solutions.append(sol)

        # --- STEP 2: Ensembe the best one ---
        best_solution = await self.sc_ensemble(solutions=solutions)

        # --- STEP 3: Critically reflect on the best solution ---
        reflection = await self.reflect(pre_solution=best_solution)

        # --- STEP 4: Branch into multiple possible improvements using FlexibleCustom ---
        # The branching pattern allows us to explore two paths: one focused on clarity, one on accuracy
        branch_solutions = []
        for branch_type in ["clarity", "accuracy"]:
            instruction = f"Based on this reflection: {reflection}. Now solve again focusing on {branch_type}."  
            branch_sol = await self.flexible_custom(
                custom_instruction=instruction,
                reasoning_pattern="branching",
                steps=["analyze_reflection", f"improve_{branch_type}", "recheck_logic"],
                use_structured_output=True
            )
            branch_solutions.append(branch_sol)

        # --- STEP 5: Pick the better branch via simple heuristic (e.g., length or confidence) ---
        # In practice, we could use another ScEnsemble here, but since only 2 branches, just compare them directly
        # For simplicity, pick the shorter one as a proxy for clarity — real-world would use more nuanced scoring
        final_candidate = min(branch_solutions, key=len)

        # --- STEP 6: Final polish with Review ---
        final_answer = await self.review(pre_solution=final_candidate)

        return final_answer