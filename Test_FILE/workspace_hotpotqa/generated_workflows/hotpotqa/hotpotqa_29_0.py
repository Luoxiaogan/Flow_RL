# Workflow ID: hotpotqa_29_0
# Benchmark: hotpotqa
# Data Indices: [3526, 2853, 2302, 1651, 1151]

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
        It uses flexible custom reasoning to break down the problem step-by-step,
        then synthesizes an answer using ensemble and review for robustness.
        """
        # Step 1: Use FlexibleCustom with sequential reasoning to extract entities and connect them
        solution1 = await self.flexible_custom(
            custom_instruction="Break down the problem into smaller steps by first extracting key entities, then finding connections between them, and finally synthesizing the answer.",
            reasoning_pattern="sequential",
            steps=["extract_entities", "find_connections", "synthesize_answer"]
        )

        # Step 2: Generate a direct answer as a baseline
        solution2 = await self.answer_generate()

        # Step 3: Ensemble the two solutions for improved accuracy
        ensemble_solution = await self.sc_ensemble(solutions=[solution1, solution2])

        # Step 4: Review the ensemble solution to refine it
        final_answer = await self.review(pre_solution=ensemble_solution)

        return final_answer