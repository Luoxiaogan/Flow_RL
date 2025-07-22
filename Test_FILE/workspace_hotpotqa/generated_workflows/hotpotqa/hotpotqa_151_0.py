# Workflow ID: hotpotqa_151_0
# Benchmark: hotpotqa
# Data Indices: [897, 3374, 1661, 1050, 3921]

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
        This is a robust workflow graph for multi-hop question answering.
        It explores multiple reasoning paths using Custom operators with step-by-step instructions,
        then ensembles the results to select the best solution. A final Review ensures quality.
        """
        # Step 1: Generate multiple solutions via different reasoning patterns
        solution1 = await self.custom(instruction="Break down the problem into smaller steps and explain each step clearly.")
        solution2 = await self.custom(instruction="Solve this by identifying key entities and tracing connections between them.")
        solution3 = await self.flexible_custom(
            custom_instruction="Use sequential reasoning to trace the logical path from given facts to the answer.",
            reasoning_pattern="sequential",
            steps=["identify_key_entities", "find_intermediate_connections", "trace_logical_path", "synthesize_final_answer"]
        )

        # Step 2: Ensemble the solutions to find the most consistent and well-supported answer
        solutions = [solution1, solution2, solution3]
        ensembled_solution = await self.sc_ensemble(solutions=solutions)

        # Step 3: Final review to refine and validate the selected solution
        final_answer = await self.review(pre_solution=ensembled_solution)

        return final_answer