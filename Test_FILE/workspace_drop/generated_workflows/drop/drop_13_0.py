# Workflow ID: drop_13_0
# Benchmark: drop
# Data Indices: [2080, 2096, 1480, 2526]

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
        This is a workflow graph optimized for step-by-step reasoning.
        It uses specialized operators based on problem type and ensures information flow.
        """
        # Step 1: Break down the problem using Custom to extract key elements
        structured_analysis = await self.custom(instruction="Break down the problem into smaller steps. Identify what needs to be counted, calculated, or compared.")

        # Step 2: Determine if it's a counting task
        if "count" in structured_analysis.lower() or "how many" in structured_analysis.lower():
            count_result = await self.counting_reasoning()
            # Review the count result for accuracy
            reviewed_count = await self.review(pre_solution=count_result)
            return reviewed_count

        # Step 3: Check for arithmetic operations
        elif any(op in structured_analysis.lower() for op in ["add", "subtract", "multiply", "sum", "difference", "product"]):
            arithmetic_result = await self.arithmetic_reasoning()
            reviewed_arithmetic = await self.review(pre_solution=arithmetic_result)
            return reviewed_arithmetic

        # Step 4: Check for comparison (max, min, greater than, etc.)
        elif any(comp in structured_analysis.lower() for comp in ["compare", "greater", "lesser", "most", "least", "higher", "lower"]):
            comparison_result = await self.comparison_reasoning()
            reviewed_comparison = await self.review(pre_solution=comparison_result)
            return reviewed_comparison

        # Step 5: If none of the above, generate a direct answer
        else:
            direct_answer = await self.answer_generate()
            # Ensemble with a custom breakdown for robustness
            custom_solution = await self.custom(instruction="Solve this by breaking it down into clear, logical steps.")
            solutions = [direct_answer, custom_solution]
            final_answer = await self.sc_ensemble(solutions=solutions)
            return final_answer