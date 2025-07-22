# Workflow ID: hotpotqa_14_0
# Benchmark: hotpotqa
# Data Indices: [570, 2742, 3873, 2851]

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
        It uses multiple reasoning paths to enhance robustness and selects the best answer via ensemble.
        """
        # Step 1: Generate initial answer using direct generation
        direct_answer = await self.answer_generate()

        # Step 2: Generate step-by-step reasoning using Custom with structured instruction
        step_by_step = await self.custom(instruction="Can you solve this problem by breaking it down into detailed steps and explaining the reasoning behind each step?")

        # Step 3: Use FlexibleCustom for iterative refinement (sequential reasoning path)
        iterative_refinement = await self.flexible_custom(
            custom_instruction="Use an iterative approach to refine your answer based on intermediate findings.",
            reasoning_pattern="iterative",
            steps=["initial_hypothesis", "verify_facts", "refine_answer"],
            max_iterations=2
        )

        # Step 4: Ensemble all solutions to select the most well-supported one
        solutions = [direct_answer, step_by_step, iterative_refinement]
        ensembled_solution = await self.sc_ensemble(solutions=solutions)

        # Step 5: Final review to improve confidence in the selected solution
        final_answer = await self.review(pre_solution=ensembled_solution)

        return final_answer