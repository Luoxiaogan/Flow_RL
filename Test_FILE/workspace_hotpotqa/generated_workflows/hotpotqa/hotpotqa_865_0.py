# Workflow ID: hotpotqa_865_0
# Benchmark: hotpotqa
# Data Indices: [2055, 171, 2515, 59, 333]

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
        It uses flexible custom reasoning to break down the problem into steps,
        then synthesizes the answer using iterative refinement and ensemble techniques.
        """
        # Step 1: Use FlexibleCustom with sequential reasoning to extract entities and connect information
        solution = await self.flexible_custom(
            custom_instruction="Break down the problem step by step, identifying key entities and connections between them.",
            reasoning_pattern="sequential",
            steps=["extract_entities", "find_connections", "synthesize_answer"]
        )

        # Step 2: Generate an initial answer using AnswerGenerate for baseline
        baseline_answer = await self.answer_generate()

        # Step 3: Ensemble the flexible custom solution with the baseline answer
        solutions = [solution, baseline_answer]
        ensembled_solution = await self.sc_ensemble(solutions=solutions)

        # Step 4: Review the ensembled solution to refine it further
        final_answer = await self.review(pre_solution=ensembled_solution)

        return final_answer