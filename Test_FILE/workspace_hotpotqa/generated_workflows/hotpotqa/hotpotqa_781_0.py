# Workflow ID: hotpotqa_781_0
# Benchmark: hotpotqa
# Data Indices: [3659, 1780, 319, 1681]

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
        This is a streamlined workflow graph for multi-hop question answering.
        It uses FlexibleCustom with sequential reasoning to break down the problem step-by-step.
        """
        # Step 1: Use flexible custom to extract entities and key information
        solution_1 = await self.flexible_custom(
            custom_instruction="Break down the problem into smaller steps by first identifying all relevant entities and their relationships.",
            reasoning_pattern="sequential",
            steps=["extract_entities", "find_connections", "trace_reasoning_path", "synthesize_answer"]
        )

        # Step 2: Generate an answer based on the structured reasoning
        solution_2 = await self.answer_generate()

        # Step 3: Review the generated answer using the structured solution from step 1
        final_solution = await self.review(pre_solution=solution_2)

        # Optional: Ensemble to improve robustness (if multiple valid solutions exist)
        solutions = [solution_1, final_solution]
        ensembled = await self.sc_ensemble(solutions=solutions)

        return ensembled