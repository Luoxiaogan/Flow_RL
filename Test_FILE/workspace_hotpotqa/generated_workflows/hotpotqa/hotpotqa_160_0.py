# Workflow ID: hotpotqa_160_0
# Benchmark: hotpotqa
# Data Indices: [3009, 1448, 3523, 1425, 2434]

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
        It breaks down the problem into smaller steps, traces connections through context,
        and refines the answer iteratively to ensure accuracy.
        """
        # Step 1: Use FlexibleCustom with sequential reasoning to trace multi-hop connections
        solution = await self.flexible_custom(
            custom_instruction="Break down the problem step-by-step, identifying key entities and how they connect across different parts of the context.",
            reasoning_pattern="sequential",
            steps=["identify_entities", "find_connections", "trace_reasoning_path", "synthesize_answer"]
        )

        # Step 2: Generate an initial answer based on the structured reasoning
        answer = await self.answer_generate()

        # Step 3: Review the generated answer to refine it
        refined_answer = await self.review(pre_solution=answer)

        # Step 4: Ensemble with the flexible custom result to improve robustness
        solutions = [refined_answer, solution]
        final_answer = await self.sc_ensemble(solutions=solutions)

        return final_answer