# Workflow ID: hotpotqa_606_0
# Benchmark: hotpotqa
# Data Indices: [2188, 1646, 3901, 621, 2955]

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
        It generates multiple reasoning paths using different instructions,
        then ensembles the best solution, and finally reviews it for accuracy.
        """
        # Step 1: Generate multiple solutions using different reasoning patterns
        solution1 = await self.custom(instruction="Can you solve this problem by breaking it down into detailed steps and explaining the reasoning behind each step?")
        solution2 = await self.custom(instruction="Explain how to solve the problem with clear reasoning for each step, focusing on connecting information across different parts of the context.")
        solution3 = await self.flexible_custom(
            custom_instruction="Focus on tracing the logical path between key pieces of evidence in the problem.",
            reasoning_pattern="sequential",
            steps=["identify_key_facts", "find_connections", "trace_reasoning_path", "synthesize_answer"]
        )

        # Step 2: Ensemble the solutions to select the best one
        solutions = [solution1, solution2, solution3]
        ensembled_solution = await self.sc_ensemble(solutions=solutions)

        # Step 3: Review the ensembled solution for final verification
        final_answer = await self.review(pre_solution=ensembled_solution)

        return final_answer