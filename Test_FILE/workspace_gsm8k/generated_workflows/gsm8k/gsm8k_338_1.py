# Workflow ID: gsm8k_338_1
# Benchmark: gsm8k
# Data Indices: [878, 995, 144]

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
        Parallel Ensemble + Final Review Workflow:
        - Generate 3 diverse solutions using different reasoning strategies (sequential, iterative, branching).
        - Use ScEnsemble to select the most consistent and accurate solution.
        - Apply a final review for clarity and completeness.
        
        This approach improves robustness by exploring multiple reasoning paths and selecting the best one — mimicking how humans solve problems with multiple perspectives.
        """
        # Step 1: Generate 3 independent solutions using FlexibleCustom with different patterns
        solutions = []
        for i in range(3):
            if i == 0:
                # Sequential: Break down the problem step-by-step
                sol = await self.flexible_custom(
                    custom_instruction="Solve this math problem by breaking it into clear, sequential steps.",
                    reasoning_pattern="sequential",
                    steps=["understand", "plan", "solve", "verify"]
                )
            elif i == 1:
                # Iterative: Start with an estimate, then refine
                sol = await self.flexible_custom(
                    custom_instruction="Begin with a rough estimate, then iteratively improve your solution.",
                    reasoning_pattern="iterative",
                    steps=["estimate", "refine", "finalize"],
                    max_iterations=2
                )
            else:
                # Branching: Consider multiple possible interpretations or methods
                sol = await self.flexible_custom(
                    custom_instruction="Explore multiple potential approaches to solving this problem. Choose the most logical path.",
                    reasoning_pattern="branching",
                    steps=["analyze_options", "select_best", "execute"]
                )
            solutions.append(sol)

        # Step 2: Use ScEnsemble to pick the best solution from the three
        best_solution = await self.sc_ensemble(solutions=solutions)

        # Step 3: Final refinement to ensure clarity, correctness, and completeness
        final_answer = await self.review(pre_solution=best_solution)

        return final_answer