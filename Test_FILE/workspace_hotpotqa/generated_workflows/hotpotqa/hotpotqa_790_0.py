# Workflow ID: hotpotqa_790_0
# Benchmark: hotpotqa
# Data Indices: [3822, 1787, 1137, 2612]

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
        # Step 1: Use FlexibleCustom with sequential pattern to trace connections step-by-step
        solution_1 = await self.flexible_custom(
            custom_instruction="Break down the problem into smaller steps and explain the reasoning behind each step.",
            reasoning_pattern="sequential",
            steps=["identify_key_entities", "find_intermediate_connections", "trace_reasoning_path", "synthesize_final_answer"]
        )

        # Step 2: Generate an answer directly for comparison
        solution_2 = await self.answer_generate()

        # Step 3: Review the initial solution to refine it
        reviewed_solution = await self.review(pre_solution=solution_1)

        # Step 4: Ensemble multiple solutions to select the best one
        ensemble_solutions = [solution_1, solution_2, reviewed_solution]
        final_answer = await self.sc_ensemble(solutions=ensemble_solutions)

        return final_answer