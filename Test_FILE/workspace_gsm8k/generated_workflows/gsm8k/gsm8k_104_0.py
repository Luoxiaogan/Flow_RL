# Workflow ID: gsm8k_104_0
# Benchmark: gsm8k
# Data Indices: [685, 82, 157]

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
        Diverse and complex workflow combining Parallel Ensemble + Reflect & Regenerate.
        This design uses multiple reasoning paths (fan-out), selects the best, then critically reflects
        to guide a final refined solution — mimicking human meta-cognition.
        """
        # Step 1: Generate 3 independent solutions via parallel ensemble (fan-out)
        solutions = []
        for _ in range(3):
            sol = await self.custom(
                instruction="Solve this math problem step-by-step. Break it into logical parts, define variables, and show all calculations clearly."
            )
            solutions.append(sol)

        # Step 2: Use ScEnsemble to pick the most accurate solution from the three
        best_solution = await self.sc_ensemble(solutions=solutions)

        # Step 3: Reflect on the best solution — identify assumptions, gaps, or alternative approaches
        reflection = await self.reflect(pre_solution=best_solution)

        # Step 4: Conditional logic based on reflection content — if reflection suggests improvement is needed, regenerate
        if "incomplete" in reflection.lower() or "assumption" in reflection.lower() or "alternative" in reflection.lower():
            # Regenerate with guidance from reflection
            final_answer = await self.custom(
                instruction=f"Given the initial solution and the following reflection: {reflection}. Now, provide a new, improved solution that addresses these points."
            )
        else:
            # If no major flaws found, use best solution as final answer
            final_answer = best_solution

        return final_answer