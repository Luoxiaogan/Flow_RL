# Workflow ID: gsm8k_177_1
# Benchmark: gsm8k
# Data Indices: [480, 849]

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
        This is a diverse and efficient workflow using a novel combination of:
        1. Parallel Ensemble (Fan-out/Fan-in) to generate multiple independent solutions
        2. Reflect-and-Regenerate pattern to refine the best candidate
        3. Iterative refinement via FlexibleCustom for deep improvement
        
        The logic differs fundamentally from the existing workflow by:
        - First generating multiple distinct approaches in parallel (not just one initial solution)
        - Using ensemble selection before any reflection (not after reflection)
        - Applying iterative refinement only to the top-performing solution (not all)
        - Avoiding direct reuse of the same prompt structure — instead, it uses structured reasoning steps
        """

        # Step 1: Generate 3 different solutions using diverse strategies
        # Each uses a unique Custom instruction to encourage varied reasoning paths
        solutions = [
            await self.custom(instruction="Solve the problem by breaking it into smaller parts first, then solving each part systematically."),
            await self.custom(instruction="Approach this as a real-world scenario: what would a person do step-by-step?"),
            await self.custom(instruction="Use dimensional analysis or unit conversion logic to solve this problem.")
        ]

        # Step 2: Use ScEnsemble to pick the most accurate solution among the three
        best_solution = await self.sc_ensemble(solutions=solutions)

        # Step 3: Critically reflect on the best solution to uncover hidden flaws or assumptions
        reflection = await self.reflect(pre_solution=best_solution)

        # Step 4: Use FlexibleCustom with an iterative reasoning pattern to refine the best solution
        # This applies a structured loop: analyze → plan → solve → verify → repeat until stable
        refined_solution = await self.flexible_custom(
            custom_instruction="Refine the solution based on the following reflection: " + reflection,
            reasoning_pattern="iterative",
            steps=["analyze", "plan", "solve", "verify"],
            max_iterations=2,
            use_structured_output=True
        )

        return refined_solution