# Workflow ID: hotpotqa_365_0
# Benchmark: hotpotqa
# Data Indices: [383, 1774, 63, 2640]

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
        Uses FlexibleCustom with structured reasoning steps to efficiently solve complex problems.
        """
        # Step 1: Use flexible custom to break down the problem using sequential multi-hop reasoning
        solution = await self.flexible_custom(
            custom_instruction="Break down the problem into smaller steps and reason through each step logically.",
            reasoning_pattern="sequential",
            steps=["extract_entities", "find_connections", "trace_reasoning_path", "synthesize_answer"]
        )

        # Step 2: Generate an answer based on the structured reasoning output
        final_answer = await self.answer_generate()

        # Step 3: Ensemble multiple solutions if needed (here we use just one, but can be extended)
        ensemble_solution = await self.sc_ensemble(solutions=[solution, final_answer])

        # Step 4: Review the ensemble result to refine accuracy
        refined_solution = await self.review(pre_solution=ensemble_solution)

        return refined_solution