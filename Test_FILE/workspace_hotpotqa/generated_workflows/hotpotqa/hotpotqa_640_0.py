# Workflow ID: hotpotqa_640_0
# Benchmark: hotpotqa
# Data Indices: [3403, 2607, 1678, 2064]

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
        It uses multiple reasoning paths and ensemble to improve accuracy.
        """
        # Generate multiple solutions using different custom instructions
        solution1 = await self.custom(instruction="Break down the problem into smaller steps and explain each step clearly.")
        solution2 = await self.custom(instruction="Solve by identifying key entities first, then tracing connections between them.")
        solution3 = await self.custom(instruction="Think step-by-step: what information is needed, how can it be linked?")
        
        # Ensemble the solutions to select the best one
        ensemble_solution = await self.sc_ensemble(solutions=[solution1, solution2, solution3])
        
        # Final review to refine the answer
        final_answer = await self.review(pre_solution=ensemble_solution)
        
        return final_answer