# Workflow ID: hotpotqa_272_0
# Benchmark: hotpotqa
# Data Indices: [1407, 3393, 2765, 2632, 2150]

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

        # Step 2: Use FlexibleCustom with sequential multi-hop reasoning to trace connections
        multi_hop_solution = await self.flexible_custom(
            custom_instruction="Focus on connecting information across different parts of the context",
            reasoning_pattern="sequential",
            steps=["identify_entities", "find_connections", "trace_reasoning_path", "synthesize_answer"]
        )

        # Step 3: Generate an answer directly as a baseline
        direct_answer = await self.answer_generate()

        # Step 4: Review the multi-hop solution to refine it
        refined_solution = await self.review(pre_solution=multi_hop_solution)

        # Step 5: Ensemble multiple solutions (direct + refined) to get the best one
        ensemble_solution = await self.sc_ensemble(solutions=[direct_answer, refined_solution])

        return ensemble_solution