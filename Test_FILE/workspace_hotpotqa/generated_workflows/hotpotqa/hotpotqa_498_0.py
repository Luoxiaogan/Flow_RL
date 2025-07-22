# Workflow ID: hotpotqa_498_0
# Benchmark: hotpotqa
# Data Indices: [3499, 2238, 2322, 34]

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
        It uses flexible custom reasoning to break down the problem into key steps,
        then synthesizes the answer effectively.
        """
        # Step 1: Use FlexibleCustom with structured multi-hop reasoning
        solution = await self.flexible_custom(
            custom_instruction="Break down the problem step-by-step using extraction, connection finding, and synthesis.",
            reasoning_pattern="sequential",
            steps=["extract_entities", "find_connections", "synthesize_answer"]
        )

        # Step 2: Optionally refine using Review if needed (e.g., for complex problems)
        refined_solution = await self.review(pre_solution=solution)

        # Step 3: Final answer generation to ensure clarity and completeness
        final_answer = await self.answer_generate()

        # Step 4: Ensemble to improve robustness (use both original and refined)
        ensemble_result = await self.sc_ensemble(solutions=[solution, refined_solution, final_answer])

        return ensemble_result