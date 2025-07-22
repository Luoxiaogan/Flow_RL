# Workflow ID: hotpotqa_442_0
# Benchmark: hotpotqa
# Data Indices: [1700, 1730, 62, 1487]

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
        It uses multiple reasoning paths and ensembles the best solution.
        """
        # Step 1: Generate initial answer directly (baseline)
        baseline_answer = await self.answer_generate()

        # Step 2: Use flexible custom to explore multi-hop reasoning via sequential path
        sequential_solution = await self.flexible_custom(
            custom_instruction="Break down the problem into smaller steps and explain each step clearly.",
            reasoning_pattern="sequential",
            steps=["identify_key_entities", "find intermediate connections", "trace logical path", "synthesize final answer"]
        )

        # Step 3: Use flexible custom to explore parallel reasoning paths
        parallel_solution = await self.flexible_custom(
            custom_instruction="Explore multiple possible reasoning paths simultaneously.",
            reasoning_pattern="parallel",
            steps=["path_one", "path_two", "path_three"]
        )

        # Step 4: Use Custom with step-by-step instruction to generate another detailed solution
        detailed_step_by_step = await self.custom(
            instruction="Can you solve this problem by breaking it down into detailed steps and explaining the reasoning behind each step?"
        )

        # Step 5: Ensemble all solutions to select the most well-supported one
        solutions = [baseline_answer, sequential_solution, parallel_solution, detailed_step_by_step]
        ensembled_answer = await self.sc_ensemble(solutions=solutions)

        # Step 6: Final review to verify and refine the ensembled answer
        final_answer = await self.review(pre_solution=ensembled_answer)

        return final_answer