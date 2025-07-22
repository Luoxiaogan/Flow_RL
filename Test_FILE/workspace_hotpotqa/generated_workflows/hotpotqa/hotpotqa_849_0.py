# Workflow ID: hotpotqa_849_0
# Benchmark: hotpotqa
# Data Indices: [2676, 1567, 688, 959, 896]

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
        It uses multiple reasoning paths and ensembles the best solution.
        """
        # Step 1: Generate initial answer using direct generation
        direct_answer = await self.answer_generate()

        # Step 2: Use flexible custom with sequential reasoning to break down the problem
        sequential_reasoning = await self.flexible_custom(
            custom_instruction="Break down the problem into smaller steps and explain the reasoning behind each step",
            reasoning_pattern="sequential",
            steps=["identify_key_entities", "find_intermediate_connections", "trace_logical_path", "synthesize_final_answer"]
        )

        # Step 3: Generate another solution using a different instruction for diverse reasoning
        step_by_step_answer = await self.custom(
            instruction="Solve this by breaking it down into detailed steps and explaining the reasoning for each."
        )

        # Step 4: Ensemble the three solutions to select the most consistent one
        solutions = [direct_answer, sequential_reasoning, step_by_step_answer]
        ensembled_solution = await self.sc_ensemble(solutions=solutions)

        # Step 5: Final review to refine and verify the selected solution
        final_answer = await self.review(pre_solution=ensembled_solution)

        return final_answer