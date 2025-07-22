# Workflow ID: gsm8k_305_1
# Benchmark: gsm8k
# Data Indices: [115, 817, 70]

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
        Diverse workflow using the Reflect and Regenerate pattern with iterative refinement via FlexibleCustom.
        This approach first generates a solution, then uses reflection to guide a structured, multi-step improvement process.
        Unlike the existing workflow, it does not rely on a single custom prompt after reflection but instead uses an iterative reasoning pattern
        that naturally incorporates feedback loops — mimicking how humans improve solutions through metacognition.
        """
        # Step 1: Generate initial solution using flexible custom in sequential mode (clear structure)
        initial_solution = await self.flexible_custom(
            reasoning_pattern="sequential",
            steps=["analyze", "plan", "solve", "verify"],
            custom_instruction="Break down the problem systematically. First, identify all known quantities. Then, determine what needs to be calculated. Finally, perform the computation and verify your result."
        )

        # Step 2: Critically reflect on the solution — focus on assumptions, clarity, and logical gaps
        reflection = await self.reflect(pre_solution=initial_solution)

        # Step 3: Use reflection to guide an iterative refinement process via FlexibleCustom in 'iterative' mode
        refined_solution = await self.flexible_custom(
            reasoning_pattern="iterative",
            steps=["initial_approach", "refine", "finalize"],
            max_iterations=2,
            custom_instruction=f"Start with the initial solution: {initial_solution}. Based on this reflection: '{reflection}', refine the approach step-by-step. Focus on addressing any identified weaknesses or ambiguities in the logic."
        )

        return refined_solution