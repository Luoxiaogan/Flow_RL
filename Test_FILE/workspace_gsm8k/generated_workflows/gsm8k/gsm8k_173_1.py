# Workflow ID: gsm8k_173_1
# Benchmark: gsm8k
# Data Indices: [239, 39, 322]

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
        This is a diverse and robust workflow using the Parallel Ensemble pattern with iterative refinement.
        It generates 3 distinct initial solutions via varied instructions, selects the best one via ensemble,
        then applies an iterative refinement loop to improve it further—mimicking expert problem-solving.
        """
        # Step 1: Generate multiple independent solutions using different reasoning styles
        solution_pool = []
        instructions = [
            "Solve this step-by-step using clear mathematical reasoning. Focus on defining variables first.",
            "Break down the problem into sub-problems and solve each in sequence. Be explicit about assumptions.",
            "Use a structured approach: identify what’s given, what’s unknown, and how they relate mathematically."
        ]
        
        for instr in instructions:
            sol = await self.custom(instruction=instr)
            solution_pool.append(sol)

        # Step 2: Use ScEnsemble to pick the most consistent and accurate solution
        best_solution = await self.sc_ensemble(solutions=solution_pool)

        # Step 3: Apply iterative refinement using Review — improves the solution through targeted critique
        refined_solution = await self.review(pre_solution=best_solution)

        # Step 4: Final check — reflect on the revised solution to catch any remaining issues
        reflection = await self.reflect(pre_solution=refined_solution)

        # Step 5: Optional final validation — if reflection suggests flaws, regenerate once more
        if "error" in reflection.lower() or "assumption" in reflection.lower():
            improved_instruction = f"Based on the reflection: '{reflection}', rewrite the solution to fix potential issues."
            final_solution = await self.custom(instruction=improved_instruction)
        else:
            final_solution = refined_solution

        return final_solution