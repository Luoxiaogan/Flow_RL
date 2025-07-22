# Workflow ID: hotpotqa_497_0
# Benchmark: hotpotqa
# Data Indices: [1843, 2387, 2230, 3178]

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
        It uses FlexibleCustom for sequential reasoning to extract and connect facts,
        then Custom to synthesize the answer, and Review to validate it.
        """
        # Step 1: Use FlexibleCustom with sequential reasoning to break down and trace connections
        solution_1 = await self.flexible_custom(
            custom_instruction="Break down the problem step by step, identify key entities, and trace logical connections between them.",
            reasoning_pattern="sequential",
            steps=["identify_entities", "find_connections", "trace_reasoning_path", "synthesize_answer"]
        )

        # Step 2: Generate an initial answer using AnswerGenerate for baseline
        solution_2 = await self.answer_generate()

        # Step 3: Synthesize the solution from flexible_custom into a coherent answer using Custom
        solution_3 = await self.custom(
            instruction="Based on the structured reasoning path, synthesize a clear and concise answer to the question."
        )

        # Step 4: Ensemble multiple solutions (from flexible_custom and direct generation) to improve accuracy
        ensemble_solutions = [solution_1, solution_2, solution_3]
        ensembled_solution = await self.sc_ensemble(solutions=ensemble_solutions)

        # Step 5: Final review to refine and validate the ensembled solution
        final_solution = await self.review(pre_solution=ensembled_solution)

        return final_solution