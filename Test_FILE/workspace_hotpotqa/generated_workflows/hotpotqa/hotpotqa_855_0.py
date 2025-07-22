# Workflow ID: hotpotqa_855_0
# Benchmark: hotpotqa
# Data Indices: [727, 2558, 371, 3784]

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
        This is a streamlined workflow graph for multi-hop question answering.
        Uses FlexibleCustom with sequential reasoning to break down the problem,
        then refines the answer through review and ensembles multiple solutions.
        """
        # Step 1: Use FlexibleCustom for structured multi-hop reasoning
        solution = await self.flexible_custom(
            custom_instruction="Break down the problem into key entities, find connections between them, and synthesize a final answer.",
            reasoning_pattern="sequential",
            steps=["extract_entities", "find_connections", "synthesize_answer"]
        )

        # Step 2: Generate an alternative direct answer for ensemble
        direct_answer = await self.answer_generate()

        # Step 3: Review the main solution for refinement
        reviewed_solution = await self.review(pre_solution=solution)

        # Step 4: Ensemble the original solution, refined version, and direct answer
        ensemble_solutions = [solution, reviewed_solution, direct_answer]
        final_answer = await self.sc_ensemble(solutions=ensemble_solutions)

        return final_answer