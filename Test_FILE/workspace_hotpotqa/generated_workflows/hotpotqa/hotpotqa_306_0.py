# Workflow ID: hotpotqa_306_0
# Benchmark: hotpotqa
# Data Indices: [2861, 2873, 286, 2700, 3033]

class Workflow:
    def __init__(
        self,
        config,
        problem
    ) -> None:
        self.problem = problem
        self.config = create(config)
        self.custom = operator.Custom(self.config, self.problem)
        self.sc_ensemble = operator.ScEnsemble(self.config, self.problem)
        self.answer_generate = operator.AnswerGenerate(self.config, self.problem)
        self.review = operator.Review(self.config, self.problem)
        self.flexible_custom = operator.FlexibleCustom(self.config, self.problem)

    async def run_workflow(self):
        """
        This is a workflow graph for multi-hop question answering.
        It uses multiple reasoning paths to enhance robustness and accuracy.
        """
        # Step 1: Generate initial answer directly
        direct_answer = await self.answer_generate()

        # Step 2: Use Custom with step-by-step instruction to generate an alternative solution
        step_by_step_solution = await self.custom(
            instruction="Break down the problem into smaller steps and explain the reasoning behind each step."
        )

        # Step 3: Use FlexibleCustom with iterative refinement for deeper reasoning
        iterative_solution = await self.flexible_custom(
            custom_instruction="Start with an initial hypothesis, verify facts, then refine the answer iteratively.",
            reasoning_pattern="iterative",
            steps=["initial_hypothesis", "verify_facts", "refine_answer"],
            max_iterations=3
        )

        # Step 4: Ensemble the three solutions to select the best one
        solutions = [direct_answer, step_by_step_solution, iterative_solution]
        ensembled_answer = await self.sc_ensemble(solutions=solutions)

        # Step 5: Final review of the ensembled answer to ensure quality
        final_answer = await self.review(pre_solution=ensembled_answer)

        return final_answer