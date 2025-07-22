# Workflow ID: hotpotqa_47_0
# Benchmark: hotpotqa
# Data Indices: [990, 3045, 2194, 2636]

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
        It breaks down the problem into steps, traces connections, and refines the answer.
        """
        # Step 1: Use flexible custom to trace multi-hop connections sequentially
        multi_hop_solution = await self.flexible_custom(
            custom_instruction="Break down the problem step-by-step, identifying key entities and tracing logical connections between them.",
            reasoning_pattern="sequential",
            steps=["identify_key_entities", "find_intermediate_connections", "trace_reasoning_path", "synthesize_final_answer"]
        )

        # Step 2: Generate an initial answer based on the structured reasoning
        initial_answer = await self.answer_generate()

        # Step 3: Review the initial answer to improve clarity and correctness
        reviewed_answer = await self.review(pre_solution=initial_answer)

        # Step 4: Ensemble multiple solutions (including original multi-hop and reviewed) to select best
        solution_list = [multi_hop_solution, reviewed_answer]
        final_solution = await self.sc_ensemble(solutions=solution_list)

        return final_solution