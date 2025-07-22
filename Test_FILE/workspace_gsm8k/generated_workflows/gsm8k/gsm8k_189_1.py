# Workflow ID: gsm8k_189_1
# Benchmark: gsm8k
# Data Indices: [610, 482]

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
        Diverse and efficient workflow using Parallel Ensemble + Reflect + Regenerate.
        This approach generates multiple initial solutions (parallel), selects the best one,
        then uses reflection to guide a targeted regeneration — mimicking how experts use diverse strategies
        and then refine based on meta-cognition.
        
        Key differences from existing:
        1. Uses parallel ensemble first (not iterative or single solution).
        2. Applies reflection only after selecting a candidate — not before or during iteration.
        3. Uses conditional logic: if reflection indicates uncertainty, it triggers a second round of ensembling with more focused prompts.
        """

        # Step 1: Generate 3 independent solutions in parallel using FlexibleCustom with different reasoning patterns
        solutions = []
        for i in range(3):
            pattern = ["sequential", "iterative", "branching"][i]
            solution = await self.flexible_custom(
                custom_instruction="Solve this math word problem by breaking it into clear steps.",
                reasoning_pattern=pattern,
                steps=["analyze", "plan", "solve", "verify"],
                max_iterations=2 if pattern == "iterative" else 1
            )
            solutions.append(solution)

        # Step 2: Use ScEnsemble to pick the best solution
        best_solution = await self.sc_ensemble(solutions=solutions)

        # Step 3: Reflect on the selected solution — identify potential weaknesses or assumptions
        reflection = await self.reflect(pre_solution=best_solution)

        # Step 4: Conditional logic — if reflection suggests ambiguity or missing detail, do a second round of ensembling
        # This is the novel control flow: not just one fix, but an intelligent retry mechanism based on reflection content
        if "uncertain" in reflection.lower() or "assumption" in reflection.lower() or "missing" in reflection.lower():
            # Second round: generate 2 new solutions using tailored instructions based on reflection
            improved_solutions = []
            for j in range(2):
                instruction = f"Re-solve the problem focusing on the following issue: {reflection}. Be precise about each step."
                improved_solution = await self.custom(instruction=instruction)
                improved_solutions.append(improved_solution)

            # Final selection: choose the best among these two
            final_solution = await self.sc_ensemble(solutions=improved_solutions)
        else:
            # If no major issues found, use the original best solution
            final_solution = best_solution

        return final_solution