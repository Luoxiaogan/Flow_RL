# Workflow ID: hotpotqa_351_0
# Benchmark: hotpotqa
# Data Indices: [3541, 1596, 3159, 296, 992]

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
        It uses multiple reasoning paths to enhance robustness and accuracy.
        """
        # Step 1: Generate initial answer using direct generation
        direct_answer = await self.answer_generate()

        # Step 2: Use flexible custom with sequential reasoning to break down the problem step-by-step
        sequential_reasoning = await self.flexible_custom(
            custom_instruction="Break down the problem into smaller steps and explain each reasoning step clearly.",
            reasoning_pattern="sequential",
            steps=["identify_key_entities", "find_intermediate_connections", "trace_logical_path", "synthesize_final_answer"]
        )

        # Step 3: Use flexible custom with iterative refinement to improve the answer through verification
        iterative_refinement = await self.flexible_custom(
            custom_instruction="Start with an initial hypothesis, then verify facts and refine your answer iteratively.",
            reasoning_pattern="iterative",
            steps=["initial_hypothesis", "verify_facts", "refine_answer"],
            max_iterations=3
        )

        # Step 4: Generate one more solution using a different custom instruction (parallel reasoning path)
        parallel_reasoning = await self.custom(
            instruction="Solve this by identifying all relevant pieces of information first, then logically connect them."
        )

        # Step 5: Ensemble the three solutions to select the best one
        solutions = [direct_answer, sequential_reasoning, iterative_refinement, parallel_reasoning]
        ensembled_solution = await self.sc_ensemble(solutions=solutions)

        # Step 6: Final review to check consistency and correctness
        final_answer = await self.review(pre_solution=ensembled_solution)

        return final_answer