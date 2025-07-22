# Workflow ID: hotpotqa_833_0
# Benchmark: hotpotqa
# Data Indices: [748, 2106, 2483, 439, 3691]

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
        It uses FlexibleCustom for structured multi-hop reasoning and ensembles solutions for robustness.
        """
        # Step 1: Use FlexibleCustom to break down the problem into key reasoning steps
        solution = await self.flexible_custom(
            custom_instruction="Break down the problem step by step using extract_entities, find_connections, and synthesize_answer",
            reasoning_pattern="sequential",
            steps=["extract_entities", "find_connections", "synthesize_answer"]
        )

        # Step 2: Generate an answer directly as a baseline
        direct_answer = await self.answer_generate()

        # Step 3: Ensemble the flexible custom solution with the direct answer
        ensemble_solution = await self.sc_ensemble(solutions=[solution, direct_answer])

        # Step 4: Review the ensemble result for refinement
        final_solution = await self.review(pre_solution=ensemble_solution)

        return final_solution