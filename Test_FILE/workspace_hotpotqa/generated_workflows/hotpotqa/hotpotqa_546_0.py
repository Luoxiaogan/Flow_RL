# Workflow ID: hotpotqa_546_0
# Benchmark: hotpotqa
# Data Indices: [2176, 3980, 1942, 214, 1171]

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
        It uses FlexibleCustom with sequential reasoning to break down the problem into steps.
        """
        # Step 1: Use flexible custom to extract entities and key facts from the problem
        solution1 = await self.flexible_custom(
            custom_instruction="Break down the problem by extracting all relevant entities and facts step-by-step.",
            reasoning_pattern="sequential",
            steps=["extract_entities", "find_connections", "trace_reasoning_path", "synthesize_answer"]
        )

        # Step 2: Generate an initial answer using direct reasoning
        solution2 = await self.answer_generate()

        # Step 3: Review the initial answer for potential errors or missing links
        reviewed_solution = await self.review(pre_solution=solution2)

        # Step 4: Ensemble the two solutions (original and reviewed) to get a robust answer
        final_solution = await self.sc_ensemble(solutions=[solution1, reviewed_solution])

        return final_solution