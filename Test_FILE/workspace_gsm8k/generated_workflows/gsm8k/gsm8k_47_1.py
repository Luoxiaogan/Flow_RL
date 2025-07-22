# Workflow ID: gsm8k_47_1
# Benchmark: gsm8k
# Data Indices: [740, 652]

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
        This workflow uses a novel combination of:
        1. Parallel Ensemble (Fan-out/Fan-in) to generate multiple distinct solution paths
        2. Reflect and Regenerate pattern on the best candidate to address hidden flaws
        3. Iterative refinement via FlexibleCustom with structured reasoning steps

        The logic is fundamentally different from the existing workflow:
        - It starts with parallel exploration (not single-step generation)
        - Uses ScEnsemble to select a winner before applying meta-reflection
        - Applies reflection only to the top candidate — not all solutions
        - Leverages FlexibleCustom in iterative mode for systematic improvement
        """

        # Step 1: Generate 3 diverse initial solutions using different prompts
        # This creates a parallel ensemble — exploring multiple strategies at once
        solution_list = []
        for i in range(3):
            instruction = f"Attempt to solve this problem using a {['logical deduction', 'algebraic approach', 'step-by-step breakdown'][i]}. Be thorough."
            solution = await self.custom(instruction=instruction)
            solution_list.append(solution)

        # Step 2: Use ScEnsemble to pick the best one based on internal evaluation
        best_solution = await self.sc_ensemble(solutions=solution_list)

        # Step 3: Critically reflect on the best solution — identify potential blind spots
        reflection = await self.reflect(pre_solution=best_solution)

        # Step 4: Use FlexibleCustom in iterative mode to refine the solution
        # This mimics an expert revisiting their work — applying structured improvements
        refined_solution = await self.flexible_custom(
            custom_instruction="Refine the solution by addressing weaknesses identified in the reflection.",
            reasoning_pattern="iterative",
            steps=["analyze", "adjust", "verify"],
            max_iterations=2,
            previous_results=[best_solution, reflection]
        )

        return refined_solution