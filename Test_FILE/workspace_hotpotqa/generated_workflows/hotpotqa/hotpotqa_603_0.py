# Workflow ID: hotpotqa_603_0
# Benchmark: hotpotqa
# Data Indices: [1999, 3335, 3220, 271, 3195]

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
        It uses multiple reasoning paths and ensemble to improve robustness.
        """
        # Generate multiple solutions using different custom instructions
        solution1 = await self.custom(instruction="Break down the problem into smaller steps and explain each step in detail.")
        solution2 = await self.custom(instruction="Identify key entities and connections between them, then reason step-by-step.")
        solution3 = await self.flexible_custom(
            custom_instruction="Use sequential reasoning to trace the logical path from question to answer.",
            reasoning_pattern="sequential",
            steps=["identify_key_entities", "find_intermediate_connections", "trace_reasoning_path", "synthesize_final_answer"]
        )

        # Ensemble the solutions to select the best one
        solutions = [solution1, solution2, solution3]
        ensembled_solution = await self.sc_ensemble(solutions=solutions)

        # Final review to refine the selected solution
        final_answer = await self.review(pre_solution=ensembled_solution)

        return final_answer