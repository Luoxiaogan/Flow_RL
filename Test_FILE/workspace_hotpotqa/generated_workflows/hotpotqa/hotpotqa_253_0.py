# Workflow ID: hotpotqa_253_0
# Benchmark: hotpotqa
# Data Indices: [2714, 899, 6, 3066, 3448]

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

        # Step 2: Generate multiple reasoning paths using Custom with different step-by-step instructions
        step_by_step_1 = await self.custom(instruction="Can you solve this problem by breaking it down into detailed steps and explaining the reasoning behind each step?")
        step_by_step_2 = await self.custom(instruction="Explain how to solve the problem with clear reasoning for each step.")
        step_by_step_3 = await self.custom(instruction="Break down the problem into smaller logical sub-problems and solve them one by one.")

        # Step 3: Ensemble all solutions (direct + step-by-step) to select the best
        solutions = [direct_answer, step_by_step_1, step_by_step_2, step_by_step_3]
        ensembled_solution = await self.sc_ensemble(solutions=solutions)

        # Step 4: Final review of the ensembled solution for refinement
        final_answer = await self.review(pre_solution=ensembled_solution)

        return final_answer