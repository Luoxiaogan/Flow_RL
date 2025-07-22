# Workflow ID: drop_289_0
# Benchmark: drop
# Data Indices: [3436, 2264, 3939, 1802]

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
        This is a workflow graph optimized for step-by-step reasoning.
        Uses specialized operators based on task type and ensembles multiple solutions.
        """
        # Step 1: Generate an initial answer using direct reasoning
        initial_answer = await self.answer_generate()

        # Step 2: Use custom reasoning to break down the problem step by step
        reasoning_steps = await self.custom(
            instruction="Break down the problem into smaller steps and explain the reasoning behind each step."
        )

        # Step 3: Use flexible custom with sequential pattern for structured step-by-step processing
        structured_solution = await self.flexible_custom(
            custom_instruction="Follow a sequential reasoning pattern to solve the problem carefully.",
            reasoning_pattern="sequential",
            steps=["extract_key_info", "identify_task_type", "apply_reasoning", "verify_solution"]
        )

        # Step 4: If the problem involves counting, use CountingReasoning
        count_result = await self.counting_reasoning()

        # Step 5: If arithmetic is needed, use ArithmeticReasoning
        arithmetic_result = await self.arithmetic_reasoning()

        # Step 6: If comparison is required, use ComparisonReasoning
        comparison_result = await self.comparison_reasoning()

        # Step 7: Ensemble all generated solutions to select the best one
        solution_list = [
            initial_answer,
            reasoning_steps,
            structured_solution,
            count_result,
            arithmetic_result,
            comparison_result
        ]
        final_solution = await self.sc_ensemble(solutions=solution_list)

        return final_solution