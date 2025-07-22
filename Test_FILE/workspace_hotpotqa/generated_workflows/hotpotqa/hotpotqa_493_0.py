# Workflow ID: hotpotqa_493_0
# Benchmark: hotpotqa
# Data Indices: [3886, 3085, 2252, 3823, 1130]

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
        This is a streamlined workflow graph for multi-hop question answering.
        It uses FlexibleCustom for structured multi-hop reasoning and ensembles solutions.
        """
        # Step 1: Use FlexibleCustom to extract entities and find connections (multi-hop reasoning)
        solution_1 = await self.flexible_custom(
            custom_instruction="Break down the problem into key entities and find logical connections between them.",
            reasoning_pattern="sequential",
            steps=["extract_entities", "find_connections", "trace_reasoning_path", "synthesize_answer"]
        )

        # Step 2: Generate an answer directly as a baseline
        solution_2 = await self.answer_generate()

        # Step 3: Ensembling both solutions to improve robustness
        ensemble_solution = await self.sc_ensemble(solutions=[solution_1, solution_2])

        # Step 4: Review the ensemble result to refine if needed
        final_solution = await self.review(pre_solution=ensemble_solution)

        return final_solution