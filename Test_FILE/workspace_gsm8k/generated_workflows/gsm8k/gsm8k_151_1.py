# Workflow ID: gsm8k_151_1
# Benchmark: gsm8k
# Data Indices: [55, 471, 664]

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
        This is a diverse and robust workflow using:
        1. Parallel Ensemble (Fan-out/Fan-in) to generate multiple independent solutions
        2. Reflect and Regenerate pattern on the best solution to improve accuracy
        3. Conditional logic based on reflection content to determine whether to proceed or retry

        Unlike the existing workflow, this one first explores multiple reasoning paths in parallel,
        then critically reflects on the top candidate before deciding whether to regenerate or finalize.
        This ensures both diversity of thought and meta-cognitive refinement — a novel combination.
        """

        # Step 1: Generate 3 independent solutions using FlexibleCustom with different reasoning patterns
        # Each uses a unique sequential strategy to encourage diverse thinking
        solutions = []
        for i in range(3):
            pattern = ["sequential", "iterative", "branching"][i % 3]
            step_list = {
                "sequential": ["understand", "analyze", "solve", "verify"],
                "iterative": ["initial_guess", "refine", "finalize"],
                "branching": ["identify_path", "choose_strategy", "execute"]
            }[pattern]

            solution = await self.flexible_custom(
                custom_instruction=f"Use {pattern} reasoning to solve the problem.",
                reasoning_pattern=pattern,
                steps=step_list
            )
            solutions.append(solution)

        # Step 2: Use ScEnsemble to select the best solution from the parallel set
        best_solution = await self.sc_ensemble(solutions=solutions)

        # Step 3: Critically reflect on the selected best solution
        reflection = await self.reflect(pre_solution=best_solution)

        # Step 4: Decide whether to regenerate based on reflection content
        # If reflection indicates uncertainty or potential flaw, regenerate; otherwise, return best
        if "uncertain" in reflection.lower() or "assumption" in reflection.lower() or "flaw" in reflection.lower():
            final_solution = await self.custom(
                instruction=f"Based on the reflection: '{reflection}'. "
                            f"Re-solve the problem from scratch using a more structured approach."
            )
        else:
            final_solution = best_solution

        return final_solution