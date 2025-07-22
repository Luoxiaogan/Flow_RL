# Workflow ID: hotpotqa_142_0
# Benchmark: hotpotqa
# Data Indices: [2526, 1186, 3758, 1357, 2662]

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
        # Step 1: Generate initial answer using direct reasoning
        direct_answer = await self.answer_generate()

        # Step 2: Generate multiple solutions using different Custom instructions (multi-hop reasoning paths)
        instructions = [
            "Can you break down the problem into smaller steps?",
            "Solve this by identifying key entities and connecting them logically.",
            "Explain how to solve the problem with clear reasoning for each step."
        ]
        solutions = []
        for instruction in instructions:
            solution = await self.custom(instruction=instruction)
            solutions.append(solution)

        # Step 3: Ensemble the solutions to select the most consistent one
        ensembled_solution = await self.sc_ensemble(solutions=solutions + [direct_answer])

        # Step 4: Review the ensembled solution for final verification
        final_answer = await self.review(pre_solution=ensembled_solution)

        return final_answer