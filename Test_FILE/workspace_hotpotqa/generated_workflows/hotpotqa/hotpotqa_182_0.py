# Workflow ID: hotpotqa_182_0
# Benchmark: hotpotqa
# Data Indices: [2773, 1256, 1146, 620]

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
        """
        # Step 1: Use FlexibleCustom for structured multi-hop reasoning
        solution = await self.flexible_custom(
            custom_instruction="Break down the problem into key entities and connections between them, then synthesize the final answer.",
            reasoning_pattern="sequential",
            steps=["extract_entities", "find_connections", "trace_reasoning_path", "synthesize_answer"]
        )

        # Step 2: Generate an alternative answer using direct generation for comparison
        alternative_solution = await self.answer_generate()

        # Step 3: Ensemble both solutions to improve accuracy
        final_answer = await self.sc_ensemble(solutions=[solution, alternative_solution])

        return final_answer