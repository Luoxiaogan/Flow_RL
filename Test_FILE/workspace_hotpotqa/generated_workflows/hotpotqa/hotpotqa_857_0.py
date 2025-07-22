# Workflow ID: hotpotqa_857_0
# Benchmark: hotpotqa
# Data Indices: [3376, 3313, 3261, 2562]

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

        # Step 2: Generate multiple reasoning paths using Custom with step-by-step instructions
        reasoning_instructions = [
            "Break down the problem into smaller steps and explain the reasoning behind each step.",
            "First identify key entities, then trace connections between them, and finally synthesize the answer.",
            "Think step by step: what must be known first? What follows next? How do they connect?"
        ]
        
        solutions = []
        for instruction in reasoning_instructions:
            solution = await self.custom(instruction=instruction)
            solutions.append(solution)

        # Step 3: Ensemble the solutions to get the most robust answer
        ensemble_answer = await self.sc_ensemble(solutions=solutions + [direct_answer])

        # Step 4: Final review to refine the ensemble result
        final_answer = await self.review(pre_solution=ensemble_answer)

        return final_answer