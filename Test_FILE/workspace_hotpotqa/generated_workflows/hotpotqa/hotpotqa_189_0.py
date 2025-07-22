# Workflow ID: hotpotqa_189_0
# Benchmark: hotpotqa
# Data Indices: [3522, 3701, 1160, 3290]

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
        then synthesizes the answer after verifying intermediate steps.
        """
        # Step 1: Use FlexibleCustom with sequential reasoning to extract entities and find connections
        solution = await self.flexible_custom(
            custom_instruction="Break down the problem into smaller steps: first identify key entities, then find relationships between them, and finally synthesize the answer.",
            reasoning_pattern="sequential",
            steps=["extract_entities", "find_connections", "synthesize_answer"]
        )

        # Step 2: Review the initial solution for correctness and refinement
        reviewed_solution = await self.review(pre_solution=solution)

        # Step 3: Generate a final answer using direct answer generation as a backup
        final_answer = await self.answer_generate()

        # Step 4: Ensemble the reviewed solution and direct answer to improve accuracy
        ensemble_result = await self.sc_ensemble(solutions=[reviewed_solution, final_answer])

        return ensemble_result