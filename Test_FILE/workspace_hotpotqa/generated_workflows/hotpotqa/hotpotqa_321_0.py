# Workflow ID: hotpotqa_321_0
# Benchmark: hotpotqa
# Data Indices: [2030, 813, 3404, 2649, 1038]

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
        This is a workflow graph for multi-hop question answering using FlexibleCustom for structured reasoning.
        """
        # Step 1: Use FlexibleCustom to extract entities and identify connections across the context
        solution1 = await self.flexible_custom(
            custom_instruction="Break down the problem into key entities and find logical connections between them.",
            reasoning_pattern="sequential",
            steps=["extract_entities", "find_connections", "trace_reasoning_path"]
        )

        # Step 2: Generate an initial answer based on the structured reasoning
        solution2 = await self.answer_generate()

        # Step 3: Ensemble the two solutions to improve robustness
        ensemble_solution = await self.sc_ensemble(solutions=[solution1, solution2])

        # Step 4: Review the ensemble result to refine the final answer
        final_answer = await self.review(pre_solution=ensemble_solution)

        return final_answer