# Workflow ID: hotpotqa_313_0
# Benchmark: hotpotqa
# Data Indices: [3245, 1560, 800, 893, 3559]

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
        This is a workflow graph for multi-hop question answering using sequential reasoning.
        """
        # Step 1: Generate an initial answer with detailed reasoning
        initial_answer = await self.answer_generate()

        # Step 2: Review the initial solution to refine it
        refined_answer = await self.review(pre_solution=initial_answer)

        # Step 3: Use flexible custom with sequential multi-hop reasoning to trace connections
        multi_hop_solution = await self.flexible_custom(
            custom_instruction="Break down the problem into smaller steps and reason through each step sequentially to connect all relevant information.",
            reasoning_pattern="sequential",
            steps=["identify_key_entities", "find_intermediate_connections", "trace_reasoning_path", "synthesize_final_answer"]
        )

        # Step 4: Ensemble multiple solutions (initial, refined, and multi-hop) for robustness
        solutions = [initial_answer, refined_answer, multi_hop_solution]
        final_answer = await self.sc_ensemble(solutions=solutions)

        return final_answer