# Workflow ID: hotpotqa_180_0
# Benchmark: hotpotqa
# Data Indices: [3875, 1925, 510, 3125, 3036]

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
        Uses FlexibleCustom with sequential reasoning to break down complex problems step-by-step.
        """
        # Step 1: Use FlexibleCustom to extract key entities and relationships from the problem
        solution1 = await self.flexible_custom(
            custom_instruction="Break down the problem by identifying all key entities and their connections.",
            reasoning_pattern="sequential",
            steps=["extract_entities", "find_connections", "trace_reasoning_path"]
        )

        # Step 2: Generate an initial answer using the structured reasoning output
        solution2 = await self.answer_generate()

        # Step 3: Ensemble both solutions to improve robustness
        ensemble_solution = await self.sc_ensemble(solutions=[solution1, solution2])

        # Step 4: Review the ensemble result to refine or confirm the final answer
        final_answer = await self.review(pre_solution=ensemble_solution)

        return final_answer