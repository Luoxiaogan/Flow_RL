# Workflow ID: hotpotqa_389_0
# Benchmark: hotpotqa
# Data Indices: [580, 1179, 2191, 2305, 30]

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
        It generates multiple reasoning paths using different Custom instructions,
        then ensembles the best solution, and finally reviews it for accuracy.
        """
        # Step 1: Generate multiple solutions using different reasoning patterns
        solution1 = await self.custom(instruction="Can you break down the problem into smaller steps and explain each step in detail?")
        solution2 = await self.custom(instruction="Solve this by identifying key entities first, then tracing connections between them.")
        solution3 = await self.flexible_custom(
            custom_instruction="Use iterative reasoning to refine your answer through verification of intermediate facts.",
            reasoning_pattern="iterative",
            steps=["identify_entities", "find_connections", "verify_facts", "derive_answer"],
            max_iterations=2
        )

        # Step 2: Ensemble the solutions to select the most consistent and well-supported one
        solutions = [solution1, solution2, solution3]
        ensembled_solution = await self.sc_ensemble(solutions=solutions)

        # Step 3: Final review to ensure correctness and clarity
        final_answer = await self.review(pre_solution=ensembled_solution)

        return final_answer