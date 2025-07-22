# Workflow ID: drop_9_0
# Benchmark: drop
# Data Indices: [3484, 2349, 3800, 995]

class Workflow:
    def __init__(
        self,
        config,
        problem
    ) -> None:
        self.problem = problem
        self.agent = create(config)
        self.custom = operator.Custom(self.agent, self.problem)
        self.sc_ensemble = operator.ScEnsemble(self.agent, self.problem)
        self.answer_generate = operator.AnswerGenerate(self.agent, self.problem)
        self.review = operator.Review(self.agent, self.problem)
        self.counting_reasoning = operator.CountingReasoning(self.agent, self.problem)
        self.arithmetic_reasoning = operator.ArithmeticReasoning(self.agent, self.problem)
        self.comparison_reasoning = operator.ComparisonReasoning(self.agent, self.problem)
        self.flexible_custom = operator.FlexibleCustom(self.agent, self.problem)

    async def run_workflow(self):
        """
        This is a workflow graph optimized for reading comprehension and discrete reasoning.
        It uses specialized operators based on problem type and ensures step-by-step reasoning.
        """
        # Step 1: Extract key information from the passage using Custom
        extraction = await self.custom(instruction="Break down the passage into relevant numerical and factual details. Focus on identifying all values related to the question.")

        # Step 2: Determine the nature of the problem (counting, arithmetic, comparison)
        reasoning_type = await self.custom(instruction="Based on the extracted facts, determine whether this problem requires counting, arithmetic computation, or comparison reasoning.")

        solution = ""
        if "counting" in reasoning_type.lower():
            # Use CountingReasoning for problems involving enumeration
            solution = await self.counting_reasoning()
        elif "arithmetic" in reasoning_type.lower():
            # Use ArithmeticReasoning for numerical calculations
            solution = await self.arithmetic_reasoning()
        elif "comparison" in reasoning_type.lower():
            # Use ComparisonReasoning for max/min or relative value tasks
            solution = await self.comparison_reasoning()
        else:
            # Fallback to flexible custom reasoning for complex or mixed cases
            solution = await self.flexible_custom(
                custom_instruction="Use sequential reasoning to extract, compute, and verify the answer step by step.",
                reasoning_pattern="sequential",
                steps=["extract_values", "identify_operation", "perform_calculation", "verify_result"]
            )

        # Step 3: Generate final answer with explanation
        final_answer = await self.answer_generate()

        return final_answer