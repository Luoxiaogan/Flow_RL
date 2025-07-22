# Workflow ID: hotpotqa_300_0
# Benchmark: hotpotqa
# Data Indices: [3058, 2290, 3095, 1374, 2786]

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
        It generates multiple reasoning paths using different Custom instructions,
        then ensembles the solutions to select the best one, and finally reviews it.
        """
        # Generate multiple reasoning paths using different step-by-step instructions
        solution1 = await self.custom(instruction="Break down the problem into smaller steps and explain each reasoning step in detail.")
        solution2 = await self.custom(instruction="Solve this by identifying key entities first, then tracing connections between them.")
        solution3 = await self.custom(instruction="Think step by step: what information must be retrieved first? Then how do you connect it?")
        
        # Ensemble the three solutions to find the most consistent answer
        ensemble_solution = await self.sc_ensemble(solutions=[solution1, solution2, solution3])
        
        # Final review to refine or validate the ensembled solution
        final_answer = await self.review(pre_solution=ensemble_solution)
        
        return final_answer