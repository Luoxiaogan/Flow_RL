# Workflow ID: hotpotqa_525_0
# Benchmark: hotpotqa
# Data Indices: [215, 1434, 2825, 634]

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
        # Step 1: Use FlexibleCustom with sequential reasoning to trace multi-hop connections
        solution1 = await self.flexible_custom(
            custom_instruction="Break down the problem into smaller steps and reason step-by-step to connect relevant information across different parts of the context.",
            reasoning_pattern="sequential",
            steps=["identify_entities", "find_connections", "trace_reasoning_path", "synthesize_answer"]
        )

        # Step 2: Generate an independent answer directly for comparison
        solution2 = await self.answer_generate()

        # Step 3: Use Custom to generate a refined solution with explicit step-by-step breakdown
        solution3 = await self.custom(instruction="Can you solve this problem by breaking it down into detailed steps and explaining the reasoning behind each step?")

        # Step 4: Ensemble the three solutions to select the best one
        ensemble_result = await self.sc_ensemble(solutions=[solution1, solution2, solution3])

        # Step 5: Review the ensembled solution to refine any remaining issues
        final_solution = await self.review(pre_solution=ensemble_result)

        return final_solution