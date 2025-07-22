# Workflow ID: gsm8k_68_1
# Benchmark: gsm8k
# Data Indices: [677, 825]

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
        Robust and diverse workflow using Parallel Ensemble with Reflective Guidance.
        Generates 3 solutions via FlexibleCustom with distinct reasoning patterns (sequential, iterative, branching),
        then uses a Reflect-based critique to guide a final custom solution — not just ensembling.
        This avoids the simple 'generate-and-select' logic of the existing workflow by introducing meta-cognitive reflection
        before finalizing the answer, making it fundamentally different in control flow and error handling.
        """

        # Step 1: Generate three diverse initial solutions using FlexibleCustom with different strategies
        solutions = []
        for i in range(3):
            if i == 0:
                # Sequential: Clear step-by-step breakdown
                sol = await self.flexible_custom(
                    custom_instruction="Solve this math problem by breaking it into logical steps.",
                    reasoning_pattern="sequential",
                    steps=["understand", "model", "compute", "check"]
                )
            elif i == 1:
                # Iterative: Start rough, refine twice
                sol = await self.flexible_custom(
                    custom_instruction="Begin with an approximate approach, then refine iteratively.",
                    reasoning_pattern="iterative",
                    steps=["rough_estimate", "improve", "finalize"],
                    max_iterations=2
                )
            else:
                # Branching: Explore multiple interpretations or paths
                sol = await self.flexible_custom(
                    custom_instruction="Consider alternative methods to solve the problem and choose the best path.",
                    reasoning_pattern="branching",
                    steps=["identify_methods", "compare", "select"]
                )
            solutions.append(sol)

        # Step 2: Use ScEnsemble to pick the most consistent and accurate one
        best_solution = await self.sc_ensemble(solutions=solutions)

        # Step 3: Critically reflect on the best solution to uncover hidden flaws or assumptions
        reflection = await self.reflect(pre_solution=best_solution)

        # Step 4: Use the reflection to guide a new, improved solution — not just review!
        final_answer = await self.custom(
            instruction=f"Based on the following reflection about the best solution:\n\n{reflection}\n\nProvide a revised, improved solution that addresses potential weaknesses."
        )

        return final_answer