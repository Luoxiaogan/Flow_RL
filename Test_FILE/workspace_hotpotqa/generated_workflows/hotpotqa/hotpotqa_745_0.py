# Workflow ID: hotpotqa_745_0
# Benchmark: hotpotqa
# Data Indices: [2735, 275, 2423, 3342, 2062]

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
        It uses multiple reasoning paths and ensembles the best solution.
        """
        # Step 1: Generate initial answer using direct generation
        direct_answer = await self.answer_generate()

        # Step 2: Generate step-by-step reasoning with Custom
        step_by_step = await self.custom(instruction="Break down the problem into smaller steps and explain the reasoning behind each step.")

        # Step 3: Use FlexibleCustom for iterative multi-hop reasoning
        iterative_reasoning = await self.flexible_custom(
            custom_instruction="Follow an iterative reasoning pattern to refine the answer based on evidence.",
            reasoning_pattern="iterative",
            steps=["initial_hypothesis", "verify_evidence", "refine_answer"],
            max_iterations=3
        )

        # Step 4: Ensemble the three solutions to select the best one
        solutions = [direct_answer, step_by_step, iterative_reasoning]
        ensembled_solution = await self.sc_ensemble(solutions=solutions)

        # Step 5: Final review to ensure correctness
        final_answer = await self.review(pre_solution=ensembled_solution)

        return final_answer