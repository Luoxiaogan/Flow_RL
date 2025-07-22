# Workflow ID: hotpotqa_613_0
# Benchmark: hotpotqa
# Data Indices: [946, 2655, 2265, 2294, 2038]

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
        It breaks down the problem into steps, traces connections, and refines the answer.
        """
        # Step 1: Use FlexibleCustom to trace multi-hop connections step-by-step
        solution = await self.flexible_custom(
            custom_instruction="Break down the problem into smaller steps and explain the reasoning behind each step.",
            reasoning_pattern="sequential",
            steps=["identify_key_entities", "find_intermediate_connections", "trace_reasoning_path", "synthesize_final_answer"]
        )

        # Step 2: Generate an initial answer based on the structured reasoning
        initial_answer = await self.answer_generate()

        # Step 3: Review the initial answer to improve clarity and correctness
        reviewed_answer = await self.review(pre_solution=initial_answer)

        # Step 4: Ensemble with original flexible_custom solution for robustness
        solutions = [solution, reviewed_answer]
        final_answer = await self.sc_ensemble(solutions=solutions)

        return final_answer