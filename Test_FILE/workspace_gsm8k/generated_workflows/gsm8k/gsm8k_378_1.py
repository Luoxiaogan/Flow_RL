# Workflow ID: gsm8k_378_1
# Benchmark: gsm8k
# Data Indices: [754, 514]

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
        This workflow uses a novel Reflect + Iterative Refinement pattern with parallel exploration.
        It diverges from the existing logic by:
        1. Using parallel ensemble to generate multiple initial solutions (fan-out),
        2. Applying reflection to each to uncover different blind spots,
        3. Then refining iteratively using the best reflection to guide a final solution — not just one pass of reflection but a meta-loop that builds on critique.
        
        This creates a deeper, more robust reasoning structure than simple generate->reflect->regenerate.
        """
        # Step 1: Generate multiple independent solutions in parallel using FlexibleCustom with "parallel" pattern
        solutions = []
        for _ in range(3):  # Three different approaches to the same problem
            sol = await self.flexible_custom(
                custom_instruction="Solve this math problem using a clear, step-by-step approach.",
                reasoning_pattern="parallel",
                steps=["understand", "model", "compute", "verify"]
            )
            solutions.append(sol)

        # Step 2: Use ScEnsemble to select the most promising solution as a base for further refinement
        best_solution = await self.sc_ensemble(solutions=solutions)

        # Step 3: Critically reflect on the best solution to uncover hidden assumptions or logical gaps
        reflection = await self.reflect(pre_solution=best_solution)

        # Step 4: Use the reflection to drive an iterative refinement loop — this is where the logic differs significantly
        # Instead of a single regen, we now iterate up to 3 times, each time applying the reflection to improve the solution
        refined_solution = best_solution
        for i in range(3):
            # Each iteration uses the reflection to guide a new Custom call, creating a feedback loop
            refined_solution = await self.custom(
                instruction=f"Based on the following reflection: '{reflection}'. Improve the current solution by addressing these points: {refined_solution}"
            )
            # Optional: After each iteration, re-reflection could occur for even deeper insight — but we keep it efficient here

        return refined_solution