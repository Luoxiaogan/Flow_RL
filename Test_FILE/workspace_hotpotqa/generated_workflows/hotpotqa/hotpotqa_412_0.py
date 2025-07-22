# Workflow ID: hotpotqa_412_0
# Benchmark: hotpotqa
# Data Indices: [1079, 148, 3377, 2831]

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
        It uses FlexibleCustom with structured reasoning steps to break down complex problems.
        """
        # Step 1: Use flexible custom to extract key entities and facts from the problem
        solution1 = await self.flexible_custom(
            custom_instruction="Break down the problem by identifying key entities, facts, and relationships.",
            reasoning_pattern="sequential",
            steps=["extract_entities", "find_connections", "trace_reasoning_path"]
        )

        # Step 2: Generate an initial answer based on the extracted structure
        solution2 = await self.answer_generate()

        # Step 3: Review the generated answer using the structured solution as context
        reviewed_solution = await self.review(pre_solution=solution2)

        # Step 4: Ensemble multiple solutions (including the structured one) for better accuracy
        ensemble_solution = await self.sc_ensemble(solutions=[solution1, reviewed_solution])

        return ensemble_solution