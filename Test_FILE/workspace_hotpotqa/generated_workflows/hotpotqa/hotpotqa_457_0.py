# Workflow ID: hotpotqa_457_0
# Benchmark: hotpotqa
# Data Indices: [1618, 588, 2602, 2871]

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
        then synthesizes the answer effectively.
        """
        # Step 1: Use FlexibleCustom with multi-hop reasoning pattern to extract entities and connections
        solution = await self.flexible_custom(
            custom_instruction="Break down the problem by first identifying key entities, then finding relationships between them, and finally synthesizing a clear answer.",
            reasoning_pattern="sequential",
            steps=["extract_entities", "find_connections", "synthesize_answer"]
        )

        # Step 2: Generate a direct answer as a fallback or alternative path
        direct_answer = await self.answer_generate()

        # Step 3: Ensemble the two solutions to improve robustness
        ensemble_solution = await self.sc_ensemble(solutions=[solution, direct_answer])

        # Step 4: Review the ensembled solution to refine if needed
        final_solution = await self.review(pre_solution=ensemble_solution)

        return final_solution