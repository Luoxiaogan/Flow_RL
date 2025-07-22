# Workflow ID: drop_239_0
# Benchmark: drop
# Data Indices: [2539, 3721, 2147, 3282, 3452]

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
        This is a workflow graph optimized for comprehensive reasoning.
        Uses multiple operators in sequence and parallel to generate robust solutions.
        """
        # Step 1: Generate initial answer
        initial_answer = await self.answer_generate()

        # Step 2: Use flexible custom with sequential reasoning for step-by-step breakdown
        seq_reasoning = await self.flexible_custom(
            custom_instruction="Break down the problem into clear, logical steps with detailed reasoning for each.",
            reasoning_pattern="sequential",
            steps=["understand_question", "extract_key_info", "apply_logic", "verify_solution"]
        )

        # Step 3: Use flexible custom with iterative refinement for accuracy
        iter_refinement = await self.flexible_custom(
            custom_instruction="Carefully count or calculate the required value, then double-check your work by refining the result.",
            reasoning_pattern="iterative",
            steps=["initial_calculation", "verify_accuracy", "refine_answer"],
            max_iterations=2
        )

        # Step 4: Ensembling multiple solutions from different approaches
        solutions = [
            initial_answer,
            seq_reasoning,
            iter_refinement,
            await self.counting_reasoning(),
            await self.arithmetic_reasoning(),
            await self.comparison_reasoning()
        ]

        # Step 5: Final ensemble to select the best solution
        final_answer = await self.sc_ensemble(solutions=solutions)

        return final_answer