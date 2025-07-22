# Workflow ID: drop_461_0
# Benchmark: drop
# Data Indices: [536, 3005, 1999, 3914, 1468]

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
        It uses specialized operators based on task type and ensembles multiple reasoning paths.
        """
        # Step 1: Use flexible custom to extract key elements from the passage in a structured way
        extracted_info = await self.flexible_custom(
            custom_instruction="Break down the passage into key events, entities, and numerical data",
            reasoning_pattern="sequential",
            steps=["extract_entities", "identify_numbers", "categorize_events"]
        )

        # Step 2: Generate initial answer using direct reasoning
        initial_answer = await self.answer_generate()

        # Step 3: Use counting reasoning if the question involves counting (e.g., field goals, tackles, etc.)
        counting_result = await self.counting_reasoning()

        # Step 4: Use arithmetic reasoning if the question involves numerical computation (e.g., point difference, totals)
        arithmetic_result = await self.arithmetic_reasoning()

        # Step 5: Use comparison reasoning if the question asks for max/min or relative values
        comparison_result = await self.comparison_reasoning()

        # Step 6: Review the initial answer with feedback from other reasoning paths
        reviewed_answer = await self.review(pre_solution=initial_answer)

        # Step 7: Ensemble all results to get the most accurate final answer
        solutions = [initial_answer, counting_result, arithmetic_result, comparison_result, reviewed_answer]
        final_answer = await self.sc_ensemble(solutions=solutions)

        return final_answer