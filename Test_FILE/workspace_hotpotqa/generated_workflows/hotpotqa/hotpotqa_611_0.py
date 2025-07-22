# Workflow ID: hotpotqa_611_0
# Benchmark: hotpotqa
# Data Indices: [504, 3997, 2651, 2888, 2521]

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
        then synthesizes the answer from extracted information.
        """
        # Step 1: Use FlexibleCustom to extract entities and find connections
        solution = await self.flexible_custom(
            custom_instruction="Break down the problem by identifying key entities and their relationships.",
            reasoning_pattern="sequential",
            steps=["extract_entities", "find_connections", "synthesize_answer"]
        )

        # Step 2: If needed, refine the solution using Review
        refined_solution = await self.review(pre_solution=solution)

        # Step 3: Optionally, generate an alternative answer for ensemble
        alt_answer = await self.answer_generate()

        # Step 4: Ensemble the two solutions to improve accuracy
        final_answer = await self.sc_ensemble(solutions=[refined_solution, alt_answer])

        return final_answer