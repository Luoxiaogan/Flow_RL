# Workflow ID: gsm8k_70_1
# Benchmark: gsm8k
# Data Indices: [515, 937, 695]

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
        This is a diverse workflow using two distinct patterns:
        1. Parallel Ensemble (Fan-out/Fan-in) to generate multiple independent solutions
        2. Reflect and Regenerate: Use the best solution from the ensemble to reflect on its weaknesses,
           then regenerate an improved version based on that reflection.

        This structure ensures robustness via diversity of initial reasoning paths,
        followed by meta-cognitive refinement — a powerful combination not used in the existing workflow.
        """

        # Step 1: Generate multiple candidate solutions in parallel using FlexibleCustom with 'parallel' pattern
        # Each solution uses a different strategy or perspective to approach the problem
        solutions = []
        strategies = [
            "Break the problem into parts and solve each systematically.",
            "Start by identifying what is being asked, then work backward from the answer.",
            "Use visual representation or diagrams to model the relationships in the problem."
        ]
        
        for i, strategy in enumerate(strategies):
            solution = await self.flexible_custom(
                custom_instruction=strategy,
                reasoning_pattern="parallel",
                steps=["analyze", "plan", "solve", "verify"],
                use_structured_output=True
            )
            solutions.append(solution)

        # Step 2: Select the best solution using ScEnsemble
        best_solution = await self.sc_ensemble(solutions=solutions)

        # Step 3: Critically reflect on the best solution to identify potential blind spots
        reflection = await self.reflect(pre_solution=best_solution)

        # Step 4: Use the reflection to guide a final regeneration step
        final_solution = await self.custom(
            instruction=f"Given the following solution and reflection:\n\nSolution: {best_solution}\n\nReflection: {reflection}\n\nNow, provide a new, improved solution that addresses any overlooked assumptions, errors, or inefficiencies identified in the reflection."
        )

        return final_solution