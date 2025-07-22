# Workflow ID: hotpotqa_539_0
# Benchmark: hotpotqa
# Data Indices: [1734, 245, 2282, 3594]

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
        Uses FlexibleCustom for structured multi-hop reasoning and ensembles solutions for robustness.
        """
        # Step 1: Use FlexibleCustom to break down the problem into key reasoning steps
        solution1 = await self.flexible_custom(
            custom_instruction="Break down the problem step-by-step using extract_entities, find_connections, and synthesize_answer",
            reasoning_pattern="sequential",
            steps=["extract_entities", "find_connections", "synthesize_answer"]
        )

        # Step 2: Generate a direct answer (baseline)
        solution2 = await self.answer_generate()

        # Step 3: Review the direct answer for potential improvements
        reviewed_solution = await self.review(pre_solution=solution2)

        # Step 4: Ensemble the two solutions to select the best one
        final_solution = await self.sc_ensemble(solutions=[solution1, reviewed_solution])

        return final_solution