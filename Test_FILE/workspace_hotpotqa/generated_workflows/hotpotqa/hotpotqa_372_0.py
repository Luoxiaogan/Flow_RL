# Workflow ID: hotpotqa_372_0
# Benchmark: hotpotqa
# Data Indices: [179, 2148, 1962, 2074, 3044]

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
        It generates multiple reasoning paths using different Custom instructions,
        then ensembles the best solution, and finally reviews it for accuracy.
        """
        # Step 1: Generate multiple reasoning paths via Custom with different step-by-step prompts
        solutions = []
        instructions = [
            "Can you break down the problem into smaller steps?",
            "Solve this by identifying key entities first, then tracing connections between them.",
            "Explain how to solve the problem with clear reasoning for each step."
        ]
        
        for instruction in instructions:
            solution = await self.custom(instruction=instruction)
            solutions.append(solution)

        # Step 2: Ensemble the best solution from multiple reasoning paths
        ensembled_solution = await self.sc_ensemble(solutions=solutions)

        # Step 3: Final review to refine or verify the ensemble result
        final_answer = await self.review(pre_solution=ensembled_solution)

        return final_answer