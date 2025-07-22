# Workflow ID: hotpotqa_369_0
# Benchmark: hotpotqa
# Data Indices: [487, 2358, 1058, 3959]

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
        It breaks down the problem into steps, traces connections across context, and refines the answer.
        """
        # Step 1: Use FlexibleCustom with sequential reasoning to trace multi-hop connections
        sequential_reasoning = await self.flexible_custom(
            custom_instruction="Break down the problem step-by-step, identifying key entities and connecting information across different parts of the context.",
            reasoning_pattern="sequential",
            steps=["identify_entities", "find_connections", "trace_reasoning_path", "synthesize_answer"]
        )

        # Step 2: Generate an initial answer based on the structured reasoning
        initial_answer = await self.answer_generate()

        # Step 3: Review the initial answer to refine it using the reasoning path
        refined_answer = await self.review(pre_solution=initial_answer)

        # Step 4: Ensemble the original reasoning path and the refined answer to ensure robustness
        ensemble_solution = await self.sc_ensemble(solutions=[sequential_reasoning, refined_answer])

        return ensemble_solution