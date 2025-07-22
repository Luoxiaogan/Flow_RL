# Workflow ID: hotpotqa_298_0
# Benchmark: hotpotqa
# Data Indices: [1642, 3291, 56, 146, 3920]

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
        It uses FlexibleCustom for structured multi-hop reasoning and ensembles solutions for robustness.
        """
        # Step 1: Use FlexibleCustom to break down the problem with sequential multi-hop reasoning
        solution = await self.flexible_custom(
            custom_instruction="Break down the problem into smaller steps using sequential reasoning.",
            reasoning_pattern="sequential",
            steps=["extract_entities", "find_connections", "trace_reasoning_path", "synthesize_answer"]
        )

        # Step 2: Generate a direct answer as a baseline (for ensemble)
        baseline_answer = await self.answer_generate()

        # Step 3: Ensemble the flexible custom solution with the baseline
        final_solution = await self.sc_ensemble(solutions=[solution, baseline_answer])

        return final_solution