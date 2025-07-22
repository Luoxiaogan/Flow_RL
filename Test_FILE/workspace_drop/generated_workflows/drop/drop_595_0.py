# Workflow ID: drop_595_0
# Benchmark: drop
# Data Indices: [1283, 2027, 3913, 1305, 2112]

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
        This is a workflow graph optimized for comprehensive reasoning.
        Uses flexible custom with sequential reasoning for step-by-step breakdown,
        then ensembles multiple solutions including direct answer generation and review.
        """
        # Step 1: Use FlexibleCustom with sequential pattern to break down the problem logically
        sequential_solution = await self.flexible_custom(
            custom_instruction="Break down the problem into logical steps with clear reasoning for each",
            reasoning_pattern="sequential",
            steps=["understand_question", "extract_key_info", "reason_step_by_step", "verify_solution"]
        )

        # Step 2: Generate an answer directly using AnswerGenerate for baseline
        direct_answer = await self.answer_generate()

        # Step 3: Review the direct answer to improve it
        reviewed_answer = await self.review(pre_solution=direct_answer)

        # Step 4: Ensemble all solutions (sequential, direct, reviewed) to select best one
        ensemble_solutions = [sequential_solution, direct_answer, reviewed_answer]
        final_solution = await self.sc_ensemble(solutions=ensemble_solutions)

        return final_solution