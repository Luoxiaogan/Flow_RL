# Workflow ID: drop_358_0
# Benchmark: drop
# Data Indices: [2279, 3779, 1509, 1472, 121]

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
        This is a comprehensive workflow graph for reading comprehension and discrete reasoning.
        It uses multiple reasoning strategies and ensembles the best solution.
        """
        # Step 1: Generate initial answer using direct reasoning
        direct_answer = await self.answer_generate()

        # Step 2: Use flexible custom with sequential reasoning for structured step-by-step breakdown
        seq_solution = await self.flexible_custom(
            custom_instruction="Break down the problem into clear steps and explain each reasoning step in detail.",
            reasoning_pattern="sequential",
            steps=["understand_question", "extract_key_info", "reason_step_by_step", "verify_consistency"]
        )

        # Step 3: Use flexible custom with parallel reasoning to explore different interpretations
        parallel_solution = await self.flexible_custom(
            custom_instruction="Consider multiple possible interpretations of the question and solve each independently.",
            reasoning_pattern="parallel",
            steps=["interpret_question", "generate_approach_a", "generate_approach_b", "compare_approaches"]
        )

        # Step 4: Review the direct answer to refine it
        reviewed_answer = await self.review(pre_solution=direct_answer)

        # Step 5: Ensemle all solutions to pick the best one
        solutions = [direct_answer, seq_solution, parallel_solution, reviewed_answer]
        final_answer = await self.sc_ensemble(solutions=solutions)

        return final_answer