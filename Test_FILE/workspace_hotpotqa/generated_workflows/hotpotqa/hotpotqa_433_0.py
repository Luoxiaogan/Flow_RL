# Workflow ID: hotpotqa_433_0
# Benchmark: hotpotqa
# Data Indices: [2121, 2355, 1136, 1694, 2017]

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
        It uses multiple reasoning paths to enhance robustness and selects the best solution via ensemble.
        """
        # Step 1: Generate an initial answer using direct generation
        direct_answer = await self.answer_generate()

        # Step 2: Use flexible custom with sequential reasoning to break down the problem
        sequential_solution = await self.flexible_custom(
            custom_instruction="Break down the problem into smaller steps and explain each reasoning step clearly.",
            reasoning_pattern="sequential",
            steps=["identify_key_entities", "find_intermediate_connections", "trace_logical_path", "synthesize_final_answer"]
        )

        # Step 3: Use flexible custom with iterative refinement for accuracy
        iterative_solution = await self.flexible_custom(
            custom_instruction="Start with an initial hypothesis and refine it through fact-checking and logical verification.",
            reasoning_pattern="iterative",
            steps=["initial_hypothesis", "verify_facts", "refine_answer"],
            max_iterations=3
        )

        # Step 4: Ensemble the three solutions to select the most consistent and well-supported one
        solutions = [direct_answer, sequential_solution, iterative_solution]
        ensembled_answer = await self.sc_ensemble(solutions=solutions)

        # Step 5: Final review to catch any inconsistencies or errors in the ensembled answer
        final_answer = await self.review(pre_solution=ensembled_answer)

        return final_answer