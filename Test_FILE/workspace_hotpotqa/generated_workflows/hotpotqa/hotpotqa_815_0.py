# Workflow ID: hotpotqa_815_0
# Benchmark: hotpotqa
# Data Indices: [1445, 2347, 2002, 1165]

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
        then ensembles the best solution and finalizes with a review.
        """
        # Step 1: Generate diverse reasoning paths via Custom operators with different step-by-step prompts
        solutions = []
        prompts = [
            "Can you break down the problem into smaller steps and explain the reasoning behind each step?",
            "Solve this by identifying key entities first, then tracing connections between them.",
            "Think step by step: what information must be found first, and how do later pieces connect?"
        ]
        
        for prompt in prompts:
            solution = await self.custom(instruction=prompt)
            solutions.append(solution)

        # Step 2: Use ScEnsemble to select the best solution from diverse reasoning paths
        ensemble_solution = await self.sc_ensemble(solutions=solutions)

        # Step 3: Review the ensembled solution for correctness and clarity
        final_answer = await self.review(pre_solution=ensemble_solution)

        return final_answer