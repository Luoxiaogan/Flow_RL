# Workflow ID: hotpotqa_405_0
# Benchmark: hotpotqa
# Data Indices: [1105, 2351, 3566, 2776]

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
        # Step 1: Use FlexibleCustom with sequential pattern to trace multi-hop connections
        solution1 = await self.flexible_custom(
            custom_instruction="Break down the problem into logical steps and trace connections between pieces of information step by step.",
            reasoning_pattern="sequential",
            steps=["identify_key_entities", "find_intermediate_connections", "trace_reasoning_path", "synthesize_final_answer"]
        )

        # Step 2: Generate an independent answer using direct reasoning
        solution2 = await self.answer_generate()

        # Step 3: Review the first solution to refine it
        reviewed_solution = await self.review(pre_solution=solution1)

        # Step 4: Ensemble the original solution, refined solution, and direct answer
        solutions = [solution1, reviewed_solution, solution2]
        final_answer = await self.sc_ensemble(solutions=solutions)

        return final_answer