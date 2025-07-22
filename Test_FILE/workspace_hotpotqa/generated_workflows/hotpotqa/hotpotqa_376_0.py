# Workflow ID: hotpotqa_376_0
# Benchmark: hotpotqa
# Data Indices: [1775, 2818, 3653, 585, 2323]

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
        This is a robust multi-hop question answering workflow.
        It generates multiple reasoning paths using different instructions,
        then ensembles the best solution, and finally reviews it for accuracy.
        """
        # Step 1: Generate multiple solutions via different reasoning patterns
        solution1 = await self.custom(instruction="Break down the problem into smaller steps and explain each step in detail.")
        solution2 = await self.flexible_custom(
            custom_instruction="Use sequential reasoning to trace connections between key pieces of information.",
            reasoning_pattern="sequential",
            steps=["identify_entities", "find_connections", "trace_reasoning_path", "synthesize_answer"]
        )
        solution3 = await self.flexible_custom(
            custom_instruction="Apply iterative refinement: start with an initial answer, verify facts, then refine.",
            reasoning_pattern="iterative",
            steps=["initial_hypothesis", "verify_facts", "refine_answer"],
            max_iterations=2
        )

        # Step 2: Ensemble the three solutions to select the most consistent and well-supported one
        solutions = [solution1, solution2, solution3]
        ensembled_solution = await self.sc_ensemble(solutions=solutions)

        # Step 3: Final review to catch any logical inconsistencies or errors
        final_answer = await self.review(pre_solution=ensembled_solution)

        return final_answer