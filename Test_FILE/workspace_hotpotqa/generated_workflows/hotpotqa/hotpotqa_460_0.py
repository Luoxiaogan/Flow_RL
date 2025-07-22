# Workflow ID: hotpotqa_460_0
# Benchmark: hotpotqa
# Data Indices: [2555, 1042, 431, 1867, 368]

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
        Uses FlexibleCustom with sequential reasoning to break down and connect information.
        """
        # Step 1: Use flexible custom to extract key entities and facts from the problem
        solution1 = await self.flexible_custom(
            custom_instruction="Break down the problem into key entities and facts step by step.",
            reasoning_pattern="sequential",
            steps=["extract_entities", "find_connections", "synthesize_answer"]
        )

        # Step 2: Generate an initial answer using direct reasoning
        solution2 = await self.answer_generate()

        # Step 3: Review the initial answer to refine it based on context
        refined_solution = await self.review(pre_solution=solution2)

        # Step 4: Ensemble the two solutions (original and refined) to get the best answer
        final_answer = await self.sc_ensemble(solutions=[solution1, refined_solution])

        return final_answer