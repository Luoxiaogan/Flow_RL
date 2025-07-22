# Workflow ID: hotpotqa_159_0
# Benchmark: hotpotqa
# Data Indices: [2, 128, 2003, 3922, 1755]

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
        # Step 1: Generate multiple reasoning paths using different Custom instructions
        solution1 = await self.custom(instruction="Break down the problem into smaller steps and explain your reasoning for each step.")
        solution2 = await self.custom(instruction="Solve this by identifying key entities and connecting them logically across the context.")
        solution3 = await self.custom(instruction="First identify all relevant facts in the context, then synthesize an answer based on those facts.")

        # Step 2: Ensemble the solutions to select the most consistent one
        ensemble_solution = await self.sc_ensemble(solutions=[solution1, solution2, solution3])

        # Step 3: Final review to refine the selected solution
        final_answer = await self.review(pre_solution=ensemble_solution)

        return final_answer