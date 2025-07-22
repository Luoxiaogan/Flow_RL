# Workflow ID: hotpotqa_779_0
# Benchmark: hotpotqa
# Data Indices: [952, 3505, 3267, 2547]

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
        # Step 1: Generate multiple solutions using different custom instructions
        solutions = []
        instructions = [
            "Break down the problem into smaller steps and explain each step in detail.",
            "Identify key entities and relationships, then trace the reasoning path to the answer.",
            "First, extract all relevant facts. Then, connect them logically to derive the answer."
        ]
        
        for instruction in instructions:
            solution = await self.custom(instruction=instruction)
            solutions.append(solution)

        # Step 2: Ensemble the solutions to select the best one
        ensemble_solution = await self.sc_ensemble(solutions=solutions)

        # Step 3: Review the ensembled solution for refinement
        final_solution = await self.review(pre_solution=ensemble_solution)

        return final_solution