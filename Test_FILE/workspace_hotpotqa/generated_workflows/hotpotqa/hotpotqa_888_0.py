# Workflow ID: hotpotqa_888_0
# Benchmark: hotpotqa
# Data Indices: [140, 506, 3831, 1217]

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
        # Step 1: Use FlexibleCustom with sequential reasoning to trace multi-hop connections
        solution = await self.flexible_custom(
            custom_instruction="Break down the problem step-by-step by identifying key entities, connecting relevant facts, and tracing the logical path to the final answer.",
            reasoning_pattern="sequential",
            steps=["identify_entities", "find_connections", "trace_reasoning_path", "synthesize_answer"]
        )

        # Step 2: Generate an answer based on the structured reasoning
        answer = await self.answer_generate()

        # Step 3: Review the generated answer to refine it using the prior reasoning
        refined_answer = await self.review(pre_solution=answer)

        # Step 4: Ensemble with the original flexible_custom solution for robustness
        solutions = [solution, refined_answer]
        final_answer = await self.sc_ensemble(solutions=solutions)

        return final_answer