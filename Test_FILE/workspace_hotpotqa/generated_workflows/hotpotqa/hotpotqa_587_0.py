# Workflow ID: hotpotqa_587_0
# Benchmark: hotpotqa
# Data Indices: [1615, 1856, 1527, 1442]

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
        # Step 1: Use FlexibleCustom with sequential pattern to trace multi-hop connections
        multi_hop_solution = await self.flexible_custom(
            custom_instruction="Break down the problem step-by-step, identifying key entities and how they connect across different pieces of information.",
            reasoning_pattern="sequential",
            steps=["identify_entities", "find_connections", "trace_reasoning_path", "synthesize_answer"]
        )

        # Step 2: Generate a direct answer as a baseline for comparison
        direct_answer = await self.answer_generate()

        # Step 3: Ensemble the two solutions to select the best one
        ensemble_solution = await self.sc_ensemble(solutions=[multi_hop_solution, direct_answer])

        # Step 4: Review the ensemble solution to refine if needed
        final_solution = await self.review(pre_solution=ensemble_solution)

        return final_solution