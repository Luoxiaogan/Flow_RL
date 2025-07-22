# Workflow ID: hotpotqa_829_0
# Benchmark: hotpotqa
# Data Indices: [1746, 3205, 3384, 3666]

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
        It uses sequential reasoning to extract and connect facts, then synthesizes the answer.
        """
        # Step 1: Use FlexibleCustom with sequential reasoning to break down the problem
        solution = await self.flexible_custom(
            custom_instruction="Break down the problem into smaller steps and explain the reasoning behind each step.",
            reasoning_pattern="sequential",
            steps=["identify_key_entities", "find_intermediate_connections", "trace_reasoning_path", "synthesize_final_answer"]
        )

        # Step 2: Use Custom to refine the solution by encouraging detailed reasoning
        refined_solution = await self.custom(
            instruction="Can you solve this problem by breaking it down into detailed steps and explaining the reasoning behind each step?"
        )

        # Step 3: Ensemble multiple solutions (including original and refined) to improve accuracy
        solutions = [solution, refined_solution]
        ensembled_solution = await self.sc_ensemble(solutions=solutions)

        # Step 4: Review the ensembled solution to validate and improve it
        final_solution = await self.review(pre_solution=ensembled_solution)

        return final_solution