# Workflow ID: drop_362_0
# Benchmark: drop
# Data Indices: [1830, 57, 2859, 1812]

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
        It uses specialized operators based on problem type and ensembles results for robustness.
        """
        # Step 1: Use flexible custom to extract and reason step-by-step
        step_by_step = await self.flexible_custom(
            custom_instruction="Break down the problem into smaller steps with clear reasoning",
            reasoning_pattern="sequential",
            steps=["extract_key_info", "identify_question_type", "apply_reasoning"]
        )

        # Step 2: Generate answer directly as baseline
        direct_answer = await self.answer_generate()

        # Step 3: Use counting, arithmetic, or comparison reasoning based on problem nature
        reasoning_types = [
            await self.counting_reasoning(),
            await self.arithmetic_reasoning(),
            await self.comparison_reasoning()
        ]

        # Step 4: Ensemble all solutions for final selection
        ensemble_candidates = [step_by_step, direct_answer] + reasoning_types
        final_solution = await self.sc_ensemble(solutions=ensemble_candidates)

        return final_solution