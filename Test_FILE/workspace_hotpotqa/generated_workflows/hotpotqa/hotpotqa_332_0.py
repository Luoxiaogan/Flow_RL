# Workflow ID: hotpotqa_332_0
# Benchmark: hotpotqa
# Data Indices: [3941, 316, 1100, 2179]

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
        It breaks down the problem step-by-step and connects information across context sources.
        """
        # Step 1: Use FlexibleCustom with sequential pattern to trace connections
        solution = await self.flexible_custom(
            custom_instruction="Break down the problem into smaller steps and explain the reasoning behind each step.",
            reasoning_pattern="sequential",
            steps=["identify_key_entities", "find_intermediate_connections", "trace_reasoning_path", "synthesize_answer"]
        )

        # Step 2: Generate an answer based on the structured reasoning
        answer = await self.answer_generate()

        # Step 3: Review the answer to refine it based on prior reasoning
        refined_answer = await self.review(pre_solution=answer)

        # Step 4: Ensemble multiple solutions (e.g., from different reasoning paths) for robustness
        solutions = [solution, answer, refined_answer]
        final_answer = await self.sc_ensemble(solutions=solutions)

        return final_answer