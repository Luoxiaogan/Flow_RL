# Workflow ID: hotpotqa_33_0
# Benchmark: hotpotqa
# Data Indices: [1364, 71, 3564, 1446]

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
        Uses FlexibleCustom for structured reasoning and ensembles solutions for robustness.
        """
        # Step 1: Use flexible custom to extract entities and trace connections in a sequential manner
        solution1 = await self.flexible_custom(
            custom_instruction="Break down the problem into key entities and connections step by step.",
            reasoning_pattern="sequential",
            steps=["extract_entities", "find_connections", "trace_reasoning_path", "synthesize_answer"]
        )

        # Step 2: Generate a direct answer as a baseline
        solution2 = await self.answer_generate()

        # Step 3: Review the initial solution to refine reasoning
        refined_solution = await self.review(pre_solution=solution1)

        # Step 4: Ensemble the two solutions (direct + refined) for better accuracy
        final_solution = await self.sc_ensemble(solutions=[solution2, refined_solution])

        return final_solution