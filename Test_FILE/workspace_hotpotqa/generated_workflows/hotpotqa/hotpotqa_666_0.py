# Workflow ID: hotpotqa_666_0
# Benchmark: hotpotqa
# Data Indices: [2396, 3478, 3264, 2531, 1715]

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
        It breaks down the problem into steps, traces connections across sources, and refines the answer.
        """
        # Step 1: Use FlexibleCustom to trace multi-hop connections sequentially
        solution = await self.flexible_custom(
            custom_instruction="Break down the problem step-by-step and trace logical connections between pieces of information.",
            reasoning_pattern="sequential",
            steps=["identify_key_entities", "find_intermediate_connections", "trace_reasoning_path", "synthesize_answer"]
        )

        # Step 2: Generate an initial answer based on the structured reasoning
        initial_answer = await self.answer_generate()

        # Step 3: Review the initial answer to refine it
        refined_answer = await self.review(pre_solution=initial_answer)

        # Step 4: Ensemble with the flexible custom result for robustness
        ensemble_solution = await self.sc_ensemble(solutions=[solution, refined_answer])

        return ensemble_solution