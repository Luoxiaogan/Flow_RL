# Workflow ID: hotpotqa_438_0
# Benchmark: hotpotqa
# Data Indices: [1685, 1629, 2933, 2869]

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
        This is a workflow graph for multi-hop question answering.
        It uses flexible custom reasoning to break down the problem into steps,
        then synthesizes the final answer.
        """
        # Step 1: Use FlexibleCustom with multi-hop reasoning pattern
        solution = await self.flexible_custom(
            custom_instruction="Break down the problem step-by-step and trace connections between entities.",
            reasoning_pattern="sequential",
            steps=["extract_entities", "find_connections", "trace_reasoning_path", "synthesize_answer"]
        )

        # Step 2: Optionally review the solution for refinement
        reviewed_solution = await self.review(pre_solution=solution)

        # Step 3: Generate final answer using the refined solution
        final_answer = await self.answer_generate()

        return final_answer