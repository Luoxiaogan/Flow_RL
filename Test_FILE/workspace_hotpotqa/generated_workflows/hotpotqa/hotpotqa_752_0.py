# Workflow ID: hotpotqa_752_0
# Benchmark: hotpotqa
# Data Indices: [1620, 3316, 2616, 3161, 1663]

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
        It breaks down the problem into steps and traces connections between pieces of information.
        """
        # Step 1: Use FlexibleCustom with sequential reasoning to trace multi-hop connections
        solution = await self.flexible_custom(
            custom_instruction="Break down the problem step-by-step, identifying key entities and how they connect across different parts of the context.",
            reasoning_pattern="sequential",
            steps=["identify_entities", "find_connections", "trace_reasoning_path", "synthesize_answer"]
        )

        # Step 2: Generate an answer based on the structured reasoning path
        final_answer = await self.answer_generate()

        # Step 3: Review the generated answer for correctness and clarity
        reviewed_answer = await self.review(pre_solution=final_answer)

        # Step 4: Ensemble multiple solutions (if needed) to improve robustness
        ensemble_solution = await self.sc_ensemble(solutions=[solution, reviewed_answer])

        return ensemble_solution