# Workflow ID: drop_337_0
# Benchmark: drop
# Data Indices: [3545, 1858, 3762, 3091]

class Workflow:
    def __init__(
        self,
        config,
        problem
    ) -> None:
        self.problem = problem
        self.problem_text = str(problem) if isinstance(problem, dict) else problem
        self.config = create(config)
        self.custom = operator.Custom(self.config, self.problem)
        self.sc_ensemble = operator.ScEnsemble(self.config, self.problem)
        self.answer_generate = operator.AnswerGenerate(self.config, self.problem)
        self.review = operator.Review(self.config, self.problem)
        self.counting_reasoning = operator.CountingReasoning(self.config, self.problem)
        self.arithmetic_reasoning = operator.ArithmeticReasoning(self.config, self.problem)
        self.comparison_reasoning = operator.ComparisonReasoning(self.config, self.problem)
        self.flexible_custom = operator.FlexibleCustom(self.config, self.problem)

    async def run_workflow(self):
        """
        This is a workflow graph optimized for reading comprehension and discrete reasoning.
        Uses step-by-step reasoning via specialized operators and ensembles multiple solutions.
        """
        # Step 1: Use flexible custom to extract and reason in structured steps
        solution1 = await self.flexible_custom(
            custom_instruction="Break down the problem into clear reasoning steps",
            reasoning_pattern="sequential",
            steps=["extract_key_values", "identify_operation", "compute_step_by_step", "verify_solution"]
        )

        # Step 2: Generate direct answer using AnswerGenerate
        solution2 = await self.answer_generate()

        # Step 3: Use Custom to generate a detailed reasoning breakdown
        solution3 = await self.custom(instruction="Solve this by breaking it down into smaller steps with clear reasoning for each")

        # Step 4: Ensemble all three solutions to select the best one
        ensemble_result = await self.sc_ensemble(solutions=[solution1, solution2, solution3])

        return ensemble_result