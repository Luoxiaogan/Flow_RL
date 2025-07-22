# Workflow ID: hotpotqa_200_0
# Benchmark: hotpotqa
# Data Indices: [230, 2308, 1743, 2089, 3002]

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
        This is a robust workflow graph for multi-hop question answering.
        It generates multiple reasoning paths using different instructions,
        then ensembles the best solution and reviews it for final verification.
        """
        # Step 1: Generate multiple reasoning paths using different Custom instructions
        solutions = []
        instructions = [
            "Break down the problem into smaller steps and explain the reasoning behind each step.",
            "Solve this by identifying key entities and tracing connections between them.",
            "First identify the core question, then find relevant context to answer it step-by-step."
        ]
        
        for instruction in instructions:
            solution = await self.custom(instruction=instruction)
            solutions.append(solution)

        # Step 2: Ensemble the solutions to select the best one
        ensemble_solution = await self.sc_ensemble(solutions=solutions)

        # Step 3: Review the ensemble solution for refinement
        final_solution = await self.review(pre_solution=ensemble_solution)

        return final_solution