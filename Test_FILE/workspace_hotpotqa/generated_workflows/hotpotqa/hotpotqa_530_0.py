# Workflow ID: hotpotqa_530_0
# Benchmark: hotpotqa
# Data Indices: [1212, 1076, 3705, 2068, 3092]

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
        It generates multiple reasoning paths using different instructions,
        then ensembles the best solution and reviews it for final verification.
        """
        # Step 1: Generate initial answer directly
        direct_answer = await self.answer_generate()

        # Step 2: Generate multiple reasoning paths via Custom with different prompts
        reasoning_paths = []
        prompts = [
            "Can you break down the problem into smaller steps?",
            "Solve this by identifying key entities and connecting them logically.",
            "Explain how to solve the problem with clear reasoning for each step."
        ]
        for prompt in prompts:
            solution = await self.custom(instruction=prompt)
            reasoning_paths.append(solution)

        # Step 3: Ensemble the solutions from reasoning paths
        ensemble_solution = await self.sc_ensemble(solutions=reasoning_paths + [direct_answer])

        # Step 4: Review the ensembled solution for refinement
        final_answer = await self.review(pre_solution=ensemble_solution)

        return final_answer