# Workflow ID: drop_0_0
# Benchmark: drop
# Data Indices: [3016, 2858, 509, 240, 767]

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
        This is a robust workflow graph using Parallel Ensemble pattern.
        Generates multiple solutions via different reasoning paths, then selects the best.
        """
        # Step 1: Generate initial solution using direct answer generation
        direct_answer = await self.answer_generate()

        # Step 2: Generate solution with step-by-step breakdown (custom reasoning)
        step_by_step = await self.custom(instruction="Can you solve this problem by breaking it down into detailed steps and explaining the reasoning behind each step?")

        # Step 3: Use flexible custom for iterative refinement (if needed for complex problems)
        refined_solution = await self.flexible_custom(
            custom_instruction="Use iterative reasoning to carefully analyze and refine the solution",
            reasoning_pattern="iterative",
            steps=["initial_analysis", "verify_consistency", "refine_answer"],
            max_iterations=2
        )

        # Step 4: Ensembling all solutions using ScEnsemble for robustness
        solutions = [direct_answer, step_by_step, refined_solution]
        final_answer = await self.sc_ensemble(solutions=solutions)

        return final_answer