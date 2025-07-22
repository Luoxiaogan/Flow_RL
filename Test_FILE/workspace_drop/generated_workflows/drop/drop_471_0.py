# Workflow ID: drop_471_0
# Benchmark: drop
# Data Indices: [985, 3672, 2906, 374]

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
        It leverages specialized operators based on problem type and ensembles multiple solutions.
        """
        # Step 1: Extract key information using Custom (step-by-step thinking)
        extraction = await self.custom(instruction="Break down the problem into smaller steps and explain the reasoning behind each step.")

        # Step 2: Generate direct answer as baseline
        baseline_answer = await self.answer_generate()

        # Step 3: Use flexible custom to apply structured reasoning patterns
        structured_solution = await self.flexible_custom(
            custom_instruction="Apply step-by-step reasoning with verification at each stage.",
            reasoning_pattern="sequential",
            steps=["extract_key_data", "identify_operation", "compute_step_by_step", "verify_result"]
        )

        # Step 4: Ensemple all solutions to select the best one
        solutions = [baseline_answer, extraction, structured_solution]
        final_answer = await self.sc_ensemble(solutions=solutions)

        return final_answer