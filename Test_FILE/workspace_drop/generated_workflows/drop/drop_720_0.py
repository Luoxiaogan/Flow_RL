# Workflow ID: drop_720_0
# Benchmark: drop
# Data Indices: [3839, 1758, 804, 3188, 1798]

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
        This is a workflow graph optimized for iterative improvement.
        Starts with direct answer generation, then refines via review.
        Ensembles multiple solutions to improve accuracy.
        """
        # Step 1: Generate initial solution
        initial_solution = await self.answer_generate()

        # Step 2: Review the initial solution to refine it
        refined_solution = await self.review(pre_solution=initial_solution)

        # Step 3: Generate alternative reasoning paths using custom prompts
        step_by_step_solution = await self.custom(
            instruction="Break down the problem into smaller steps and explain the reasoning behind each step."
        )

        # Step 4: Use flexible custom for structured reasoning (sequential pattern)
        structured_solution = await self.flexible_custom(
            custom_instruction="Follow a structured approach: extract key facts, identify relationships, apply logic, verify conclusion.",
            reasoning_pattern="sequential",
            steps=["extract_facts", "identify_relationships", "apply_logic", "verify_conclusion"]
        )

        # Step 5: Ensemble all generated solutions to select the best one
        solutions = [initial_solution, refined_solution, step_by_step_solution, structured_solution]
        final_answer = await self.sc_ensemble(solutions=solutions)

        return final_answer