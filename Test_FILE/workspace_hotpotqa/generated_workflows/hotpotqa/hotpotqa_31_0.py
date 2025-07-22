# Workflow ID: hotpotqa_31_0
# Benchmark: hotpotqa
# Data Indices: [1061, 2709, 1051, 3760]

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

        # Step 2: Use flexible custom with sequential reasoning to trace multi-hop logic
        sequential_solution = await self.flexible_custom(
            custom_instruction="Break down the problem into smaller steps and explain reasoning for each step",
            reasoning_pattern="sequential",
            steps=["identify_key_entities", "find_intermediate_connections", "trace_reasoning_path", "synthesize_final_answer"]
        )

        # Step 3: Use flexible custom with iterative refinement for accuracy
        iterative_solution = await self.flexible_custom(
            custom_instruction="Start with an initial answer, then verify against context and refine",
            reasoning_pattern="iterative",
            steps=["initial_hypothesis", "verify_facts", "refine_answer"],
            max_iterations=3
        )

        # Step 4: Generate another solution using a different custom instruction (parallel path)
        parallel_solution = await self.custom(
            instruction="Solve this by identifying all relevant facts first, then connecting them logically"
        )

        # Step 5: Ensemble all solutions to select the best one
        solutions = [direct_answer, sequential_solution, iterative_solution, parallel_solution]
        final_answer = await self.sc_ensemble(solutions=solutions)

        # Step 6: Final review to ensure robustness
        final_output = await self.review(pre_solution=final_answer)

        return final_output