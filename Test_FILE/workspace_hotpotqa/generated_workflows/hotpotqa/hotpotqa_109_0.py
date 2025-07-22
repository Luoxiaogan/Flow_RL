# Workflow ID: hotpotqa_109_0
# Benchmark: hotpotqa
# Data Indices: [509, 1355, 50, 745]

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
        This is a streamlined workflow for multi-hop question answering using FlexibleCustom
        to break down the problem into key reasoning steps: extract_entities, find_connections,
        and synthesize_answer. The solution is refined via review and ensemble for robustness.
        """
        # Step 1: Use FlexibleCustom with sequential reasoning to trace multi-hop connections
        solution = await self.flexible_custom(
            custom_instruction="Break down the problem step-by-step: first extract key entities, then find logical connections between them, and finally synthesize a coherent answer.",
            reasoning_pattern="sequential",
            steps=["extract_entities", "find_connections", "synthesize_answer"]
        )

        # Step 2: Review the generated solution for consistency and clarity
        reviewed_solution = await self.review(pre_solution=solution)

        # Step 3: Generate an alternative direct answer for ensembling
        direct_answer = await self.answer_generate()

        # Step 4: Ensemble the original and reviewed solutions with the direct answer
        ensemble_solutions = [solution, reviewed_solution, direct_answer]
        final_answer = await self.sc_ensemble(solutions=ensemble_solutions)

        return final_answer