# Workflow ID: drop_10_0
# Benchmark: drop
# Data Indices: [2426, 1275, 3371, 3046, 1225]

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
        This is a workflow graph optimized for comprehensive reasoning.
        It uses step-by-step breakdowns, multiple solution paths, and ensemble selection.
        """
        # Step 1: Break down the problem into steps using FlexibleCustom (sequential pattern)
        step_by_step_analysis = await self.flexible_custom(
            custom_instruction="Break down the problem into clear, logical steps with detailed reasoning for each.",
            reasoning_pattern="sequential",
            steps=["understand_question", "extract_key_info", "identify_operations", "compute_solution"]
        )

        # Step 2: Generate initial answer from the structured analysis
        initial_answer = await self.answer_generate()

        # Step 3: Use Custom to refine reasoning if needed
        refined_reasoning = await self.custom(
            instruction="Can you solve this problem by breaking it down into detailed steps and explaining the reasoning behind each step?"
        )

        # Step 4: Ensembling multiple solutions for robustness
        solutions = [
            await self.answer_generate(),
            await self.counting_reasoning(),
            await self.arithmetic_reasoning(),
            await self.comparison_reasoning()
        ]
        ensembled_answer = await self.sc_ensemble(solutions=solutions)

        # Step 5: Review the best solution for potential improvements
        final_answer = await self.review(pre_solution=ensembled_answer)

        return final_answer