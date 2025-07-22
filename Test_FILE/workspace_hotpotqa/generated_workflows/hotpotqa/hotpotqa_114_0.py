# Workflow ID: hotpotqa_114_0
# Benchmark: hotpotqa
# Data Indices: [2666, 3993, 2378, 3429, 3839]

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
        # Step 1: Generate initial answer using direct generation
        direct_answer = await self.answer_generate()

        # Step 2: Generate multiple reasoning paths using Custom with step-by-step instructions
        reasoning_paths = []
        instructions = [
            "Can you break down the problem into smaller steps?",
            "Solve this by identifying key entities first, then connecting them logically.",
            "Explain how to solve the problem with clear reasoning for each step."
        ]
        for instr in instructions:
            solution = await self.custom(instruction=instr)
            reasoning_paths.append(solution)

        # Step 3: Ensemble the solutions from different reasoning paths
        ensemble_solution = await self.sc_ensemble(solutions=reasoning_paths + [direct_answer])

        # Step 4: Review the ensembled solution to refine it
        final_solution = await self.review(pre_solution=ensemble_solution)

        return final_solution