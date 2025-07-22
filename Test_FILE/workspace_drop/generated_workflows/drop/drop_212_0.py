# Workflow ID: drop_212_0
# Benchmark: drop
# Data Indices: [903, 2075, 3163, 2546]

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
        This is a workflow graph optimized for step-by-step reasoning in reading comprehension and discrete tasks.
        It leverages specialized operators based on task type and uses ensemble to improve robustness.
        """
        # Step 1: Use Custom to extract key elements from the passage
        extracted_info = await self.custom(instruction="Break down the passage into key facts relevant to the question. Focus on explicit statements and numerical data.")

        # Step 2: Use Counting/Arithmetic/Comparison Reasoning based on problem type (no conditionals — let operators decide internally)
        counting_result = await self.counting_reasoning()
        arithmetic_result = await self.arithmetic_reasoning()
        comparison_result = await self.comparison_reasoning()

        # Step 3: Generate initial answer using direct reasoning
        initial_answer = await self.answer_generate()

        # Step 4: Review the initial answer to refine it
        reviewed_answer = await self.review(pre_solution=initial_answer)

        # Step 5: Ensemble multiple solutions for better accuracy
        solution_list = [
            extracted_info,
            counting_result,
            arithmetic_result,
            comparison_result,
            initial_answer,
            reviewed_answer
        ]
        final_answer = await self.sc_ensemble(solutions=solution_list)

        return final_answer