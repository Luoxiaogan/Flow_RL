# Workflow ID: hotpotqa_850_0
# Benchmark: hotpotqa
# Data Indices: [1641, 908, 1723, 40]

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
        # Step 1: Use FlexibleCustom to perform multi-hop reasoning
        solution = await self.flexible_custom(
            custom_instruction="Break down the problem step by step using extract_entities, find_connections, and synthesize_answer.",
            reasoning_pattern="sequential",
            steps=["extract_entities", "find_connections", "synthesize_answer"]
        )

        # Step 2: Optionally review the generated solution for refinement
        reviewed_solution = await self.review(pre_solution=solution)

        # Step 3: Generate final answer based on refined solution
        final_answer = await self.answer_generate()

        # Step 4: Ensemble with original solution if needed (optional improvement)
        ensemble_result = await self.sc_ensemble(solutions=[solution, reviewed_solution, final_answer])

        return ensemble_result