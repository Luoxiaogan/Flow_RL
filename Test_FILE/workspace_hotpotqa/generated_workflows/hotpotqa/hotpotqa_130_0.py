# Workflow ID: hotpotqa_130_0
# Benchmark: hotpotqa
# Data Indices: [138, 2024, 753, 1888, 1906]

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
        # Step 1: Use FlexibleCustom with sequential pattern to trace multi-hop connections step-by-step
        sequential_reasoning = await self.flexible_custom(
            custom_instruction="Break down the problem into smaller steps and explain each reasoning step in detail.",
            reasoning_pattern="sequential",
            steps=["identify_key_entities", "find_intermediate_connections", "trace_logical_path", "synthesize_final_answer"]
        )

        # Step 2: Generate an initial answer based on the structured reasoning
        initial_answer = await self.answer_generate()

        # Step 3: Review the initial answer to refine it using feedback from reasoning
        refined_answer = await self.review(pre_solution=initial_answer)

        # Step 4: Ensemble multiple solutions (including original and refined) to improve robustness
        solution_list = [sequential_reasoning, initial_answer, refined_answer]
        final_solution = await self.sc_ensemble(solutions=solution_list)

        return final_solution