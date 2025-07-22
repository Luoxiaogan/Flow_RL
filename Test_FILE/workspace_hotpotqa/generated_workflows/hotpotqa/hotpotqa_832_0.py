# Workflow ID: hotpotqa_832_0
# Benchmark: hotpotqa
# Data Indices: [1873, 2018, 3996, 2096]

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
        It uses FlexibleCustom with sequential reasoning to break down the problem,
        then synthesizes the answer using a structured approach.
        """
        # Step 1: Use FlexibleCustom for structured multi-hop reasoning
        solution = await self.flexible_custom(
            custom_instruction="Break down the problem into smaller steps and reason through each step logically.",
            reasoning_pattern="sequential",
            steps=["extract_entities", "find_connections", "trace_reasoning_path", "synthesize_answer"]
        )

        # Step 2: Optionally refine using Review if needed
        refined_solution = await self.review(pre_solution=solution)

        # Step 3: Final answer generation (as fallback or confirmation)
        final_answer = await self.answer_generate()

        # Ensemble the refined solution and direct answer for robustness
        ensemble_result = await self.sc_ensemble(solutions=[refined_solution, final_answer])

        return ensemble_result