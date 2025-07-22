# Workflow ID: drop_231_0
# Benchmark: drop
# Data Indices: [1510, 663, 2418, 1096, 1689]

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
        This is a comprehensive reasoning workflow that uses multiple operators
        to handle diverse reading comprehension and discrete reasoning tasks.
        It leverages sequential, iterative, and parallel reasoning patterns
        to ensure robustness and accuracy across different problem types.
        """

        # Step 1: Generate initial answer using direct reasoning
        initial_answer = await self.answer_generate()

        # Step 2: Use flexible custom with sequential reasoning for structured step-by-step breakdown
        sequential_solution = await self.flexible_custom(
            custom_instruction="Break down the problem into clear, logical steps with detailed reasoning for each.",
            reasoning_pattern="sequential",
            steps=["understand_question", "extract_relevant_info", "reason_step_by_step", "verify_consistency"]
        )

        # Step 3: Use flexible custom with iterative refinement for complex counting or arithmetic problems
        iterative_solution = await self.flexible_custom(
            custom_instruction="Carefully count or calculate by refining your answer in multiple passes.",
            reasoning_pattern="iterative",
            steps=["initial_estimation", "cross_check", "refine"],
            max_iterations=3
        )

        # Step 4: Use parallel approach to generate alternative solutions via different reasoning paths
        parallel_solutions = [
            await self.custom(instruction="Solve this by first identifying all numerical values and then applying arithmetic logic."),
            await self.custom(instruction="Solve this by focusing on comparing percentages and their relationships."),
            await self.arithmetic_reasoning(),
            await self.counting_reasoning(),
            await self.comparison_reasoning()
        ]

        # Step 5: Ensemble all solutions to select the best one
        ensemble_result = await self.sc_ensemble(solutions=[
            initial_answer,
            sequential_solution,
            iterative_solution,
            *parallel_solutions
        ])

        # Step 6: Final review of the ensembled solution to catch any remaining errors
        final_answer = await self.review(pre_solution=ensemble_result)

        return final_answer