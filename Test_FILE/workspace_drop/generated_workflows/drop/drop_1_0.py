# Workflow ID: drop_1_0
# Benchmark: drop
# Data Indices: [2083, 2172, 2837, 1710]

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
        It uses step-by-step reasoning with specialized operators based on task type.
        """
        # Step 1: Use Custom to extract key information from the passage
        initial_analysis = await self.custom(instruction="Break down the problem into smaller steps and explain the reasoning behind each step.")

        # Step 2: Determine if the problem requires counting, arithmetic, or comparison
        reasoning_type = await self.custom(instruction="Identify whether this problem involves counting, arithmetic computation, or comparison of values.")

        # Step 3: Apply specialized reasoning based on type
        if "counting" in reasoning_type.lower():
            solution = await self.counting_reasoning()
        elif "arithmetic" in reasoning_type.lower():
            solution = await self.arithmetic_reasoning()
        elif "comparison" in reasoning_type.lower():
            solution = await self.comparison_reasoning()
        else:
            # Default fallback: use flexible custom for complex reasoning
            solution = await self.flexible_custom(
                custom_instruction="Apply sequential reasoning: extract relevant values, determine operations, perform calculations, and verify results.",
                reasoning_pattern="sequential",
                steps=["extract_values", "identify_operation", "perform_calculation", "verify_result"]
            )

        # Step 4: Generate final answer using the solution from reasoning
        final_answer = await self.answer_generate()

        return final_answer