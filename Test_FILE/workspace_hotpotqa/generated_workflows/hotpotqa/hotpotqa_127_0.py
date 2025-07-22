# Workflow ID: hotpotqa_127_0
# Benchmark: hotpotqa
# Data Indices: [964, 1582, 1005, 885, 1173]

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
        It uses flexible custom reasoning to break down the problem into steps: extract_entities, find_connections, synthesize_answer.
        """
        # Step 1: Use FlexibleCustom with sequential reasoning to trace multi-hop connections
        solution = await self.flexible_custom(
            custom_instruction="Break down the problem step-by-step: first identify key entities, then find connections between them, and finally synthesize the answer.",
            reasoning_pattern="sequential",
            steps=["extract_entities", "find_connections", "synthesize_answer"]
        )

        # Step 2: Generate an alternative direct answer using AnswerGenerate for ensemble
        alt_solution = await self.answer_generate()

        # Step 3: Ensemble both solutions to improve accuracy
        final_solution = await self.sc_ensemble(solutions=[solution, alt_solution])

        return final_solution