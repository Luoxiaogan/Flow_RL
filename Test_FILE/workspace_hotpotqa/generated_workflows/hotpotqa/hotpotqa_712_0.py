# Workflow ID: hotpotqa_712_0
# Benchmark: hotpotqa
# Data Indices: [2867, 3856, 3182, 385]

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
        then synthesizes an answer based on extracted connections.
        """
        # Step 1: Use FlexibleCustom to perform structured multi-hop reasoning
        solution = await self.flexible_custom(
            custom_instruction="Break down the problem into key entities and connections between them.",
            reasoning_pattern="sequential",
            steps=["extract_entities", "find_connections", "trace_reasoning_path", "synthesize_answer"]
        )

        # Step 2: Optionally review the solution for refinement
        reviewed_solution = await self.review(pre_solution=solution)

        # Step 3: Ensembling with direct answer generation for robustness
        direct_answer = await self.answer_generate()
        ensemble_input = [reviewed_solution, direct_answer]
        final_answer = await self.sc_ensemble(solutions=ensemble_input)

        return final_answer