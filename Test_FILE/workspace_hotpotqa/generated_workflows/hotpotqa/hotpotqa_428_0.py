# Workflow ID: hotpotqa_428_0
# Benchmark: hotpotqa
# Data Indices: [2215, 517, 360, 889]

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
        It first breaks down the problem, then traces connections step-by-step, and finally ensembles the best solution.
        """
        # Step 1: Break down the problem into smaller steps
        decomposition = await self.custom(instruction="Can you break down the problem into smaller steps?")

        # Step 2: Use FlexibleCustom with sequential reasoning to trace multi-hop connections
        multi_hop_solution = await self.flexible_custom(
            custom_instruction="Focus on connecting information across different parts of the context",
            reasoning_pattern="sequential",
            steps=["identify_entities", "find_connections", "trace_reasoning_path", "synthesize_answer"]
        )

        # Step 3: Generate a direct answer for comparison
        direct_answer = await self.answer_generate()

        # Step 4: Review the multi-hop solution to refine it
        refined_solution = await self.review(pre_solution=multi_hop_solution)

        # Step 5: Ensemble the direct answer and refined solution to get the best output
        final_answer = await self.sc_ensemble(solutions=[direct_answer, refined_solution])

        return final_answer