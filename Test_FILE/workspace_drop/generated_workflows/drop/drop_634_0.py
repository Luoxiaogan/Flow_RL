# Workflow ID: drop_634_0
# Benchmark: drop
# Data Indices: [2005, 2727, 586, 2604, 55]

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
        It uses step-by-step reasoning with specialized operators and ensembles multiple solutions.
        """
        # Step 1: Use Custom to extract key information from the passage
        extracted_info = await self.custom(instruction="Break down the passage into key facts relevant to answering the question.")

        # Step 2: Generate initial answer using AnswerGenerate
        initial_answer = await self.answer_generate()

        # Step 3: If the problem involves counting, use CountingReasoning
        counting_result = await self.counting_reasoning()

        # Step 4: If arithmetic is needed, use ArithmeticReasoning
        arithmetic_result = await self.arithmetic_reasoning()

        # Step 5: If comparison is required, use ComparisonReasoning
        comparison_result = await self.comparison_reasoning()

        # Step 6: Use FlexibleCustom for complex reasoning patterns (sequential or iterative)
        refined_solution = await self.flexible_custom(
            custom_instruction="Use sequential reasoning to verify each step of your solution.",
            reasoning_pattern="sequential",
            steps=["extract_relevant_data", "apply_logic", "validate_steps"]
        )

        # Step 7: Ensemble all candidate solutions
        solutions = [initial_answer, counting_result, arithmetic_result, comparison_result, refined_solution]
        final_solution = await self.sc_ensemble(solutions=solutions)

        # Step 8: Review the best solution to ensure correctness
        final_answer = await self.review(pre_solution=final_solution)

        return final_answer