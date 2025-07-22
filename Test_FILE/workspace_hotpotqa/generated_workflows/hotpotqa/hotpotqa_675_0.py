# Workflow ID: hotpotqa_675_0
# Benchmark: hotpotqa
# Data Indices: [1270, 2102, 3165, 2859]

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
        This is a workflow graph for multi-hop question answering using sequential reasoning.
        """
        # Step 1: Use FlexibleCustom to trace multi-hop connections step-by-step
        solution = await self.flexible_custom(
            custom_instruction="Break down the problem into smaller steps and reason through each connection sequentially.",
            reasoning_pattern="sequential",
            steps=["identify_key_entities", "find_intermediate_connections", "trace_reasoning_path", "synthesize_final_answer"]
        )

        # Step 2: Generate an answer based on the structured reasoning
        answer = await self.answer_generate()

        # Step 3: Ensemble multiple solutions (generate two different approaches)
        solution1 = await self.custom(instruction="Solve this problem by breaking it down into detailed steps and explaining the reasoning behind each step.")
        solution2 = await self.custom(instruction="Explain how to solve the problem with clear reasoning for each step.")
        ensemble = await self.sc_ensemble(solutions=[solution1, solution2, answer])

        # Step 4: Review the final ensemble result for refinement
        final_answer = await self.review(pre_solution=ensemble)

        return final_answer