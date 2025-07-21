# Workflow ID: gsm8k_52_1
# Benchmark: gsm8k
# Data Indices: [627, 193]

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
        This workflow combines two distinct patterns:
        1. Iterative Refinement (initial solution → review → refine)
        2. Reflect-and-Regenerate (critique the refined solution to guide a final overhaul)
        
        It starts with an initial attempt using sequential reasoning, then refines it iteratively.
        After refinement, it uses reflection to critique the result, which guides a final custom generation
        that synthesizes both the improved logic and meta-cognitive insights.
        """
        # Step 1: Initial solution via sequential breakdown
        initial_solution = await self.flexible_custom(
            custom_instruction="Break down the problem step-by-step with clear reasoning.",
            reasoning_pattern="sequential",
            steps=["analyze", "plan", "solve", "verify"]
        )

        # Step 2: Iterative refinement — improve the initial solution twice
        current_solution = initial_solution
        for _ in range(2):
            current_solution = await self.review(pre_solution=current_solution)

        # Step 3: Reflect on the refined solution — identify hidden assumptions or missed angles
        reflection = await self.reflect(pre_solution=current_solution)

        # Step 4: Regenerate using reflection as a guide — this is the key innovation
        final_answer = await self.custom(
            instruction=f"Based on the following reflection about the previous solution:\n{reflection}\n\n"
                       f"Provide a new, comprehensive solution that addresses any overlooked aspects and improves clarity and correctness."
        )

        return final_answer