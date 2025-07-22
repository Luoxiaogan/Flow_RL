# Workflow ID: drop_654_0
# Benchmark: drop
# Data Indices: [3935, 3068, 941, 296, 3013]

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
        Uses step-by-step reasoning with specialized operators based on problem type.
        """
        # Step 1: Use flexible custom to extract key facts from the passage in a structured way
        extraction = await self.flexible_custom(
            custom_instruction="Extract all relevant numerical and factual information from the passage in a structured format.",
            reasoning_pattern="sequential",
            steps=["identify_key_entities", "extract_numerical_values", "organize_for_reasoning"]
        )

        # Step 2: Use Custom to generate a detailed, step-by-step solution plan
        reasoning_plan = await self.custom(
            instruction="Break down the problem into smaller logical steps. Explain each step clearly, focusing on how to derive the answer from the passage."
        )

        # Step 3: Generate initial answer using direct reasoning
        initial_answer = await self.answer_generate()

        # Step 4: Use Counting/Arithmetic/Comparison Reasoning as needed based on problem type
        counting_result = await self.counting_reasoning()
        arithmetic_result = await self.arithmetic_reasoning()
        comparison_result = await self.comparison_reasoning()

        # Step 5: Ensemble multiple solutions for robustness
        solutions = [initial_answer, counting_result, arithmetic_result, comparison_result]
        final_solution = await self.sc_ensemble(solutions=solutions)

        # Step 6: Review the final solution for clarity and correctness
        refined_solution = await self.review(pre_solution=final_solution)

        return refined_solution