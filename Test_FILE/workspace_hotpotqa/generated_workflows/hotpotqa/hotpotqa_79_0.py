# Workflow ID: hotpotqa_79_0
# Benchmark: hotpotqa
# Data Indices: [3338, 2353, 2084, 53, 308]

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
        It uses FlexibleCustom for structured reasoning and ensembles solutions for robustness.
        """
        # Step 1: Use FlexibleCustom to break down the problem into structured steps
        multi_hop_solution = await self.flexible_custom(
            custom_instruction="Break down the problem step by step using structured reasoning.",
            reasoning_pattern="sequential",
            steps=["extract_entities", "find_connections", "trace_reasoning_path", "synthesize_answer"]
        )

        # Step 2: Generate an answer directly as a baseline
        direct_answer = await self.answer_generate()

        # Step 3: Review the multi-hop solution for refinement
        refined_solution = await self.review(pre_solution=multi_hop_solution)

        # Step 4: Ensemble multiple solutions (direct + refined) to improve accuracy
        solutions = [direct_answer, refined_solution]
        final_answer = await self.sc_ensemble(solutions=solutions)

        return final_answer