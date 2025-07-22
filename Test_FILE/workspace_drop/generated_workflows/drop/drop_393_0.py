# Workflow ID: drop_393_0
# Benchmark: drop
# Data Indices: [2433, 638, 2082, 1963]

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
        This is a comprehensive reasoning workflow that combines multiple operators
        to handle diverse reading comprehension and discrete reasoning tasks.
        """
        # Step 1: Generate an initial answer using direct reasoning
        initial_answer = await self.answer_generate()

        # Step 2: Use flexible custom with sequential reasoning for detailed step-by-step breakdown
        step_by_step_analysis = await self.flexible_custom(
            custom_instruction="Break down the problem into smaller steps and explain the reasoning behind each step",
            reasoning_pattern="sequential",
            steps=["identify_key_entities", "extract_relevant_information", "reason_step_by_step", "validate_conclusion"]
        )

        # Step 3: Generate a second solution via Custom agent with structured reasoning
        structured_answer = await self.custom(
            instruction="Solve this problem by breaking it down into detailed steps and explaining the reasoning behind each step"
        )

        # Step 4: Ensemble all solutions to select the best one
        solutions = [initial_answer, step_by_step_analysis, structured_answer]
        final_solution = await self.sc_ensemble(solutions=solutions)

        return final_solution