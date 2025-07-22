# Workflow ID: hotpotqa_600_0
# Benchmark: hotpotqa
# Data Indices: [2982, 2648, 1880, 2043, 2123]

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
        then synthesizes the final answer.
        """
        # Step 1: Use FlexibleCustom for structured multi-hop reasoning
        solution = await self.flexible_custom(
            custom_instruction="Break down the problem step by step using entity extraction, connection finding, and synthesis.",
            reasoning_pattern="sequential",
            steps=["extract_entities", "find_connections", "trace_reasoning_path", "synthesize_answer"]
        )

        # Step 2: Optionally refine using Review if needed
        refined_solution = await self.review(pre_solution=solution)

        # Step 3: Final Answer Generation (as fallback or validation)
        final_answer = await self.answer_generate()

        # Step 4: Ensemble to ensure robustness (if multiple paths exist)
        ensemble_result = await self.sc_ensemble(solutions=[refined_solution, final_answer])

        return ensemble_result