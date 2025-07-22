# Workflow ID: hotpotqa_74_0
# Benchmark: hotpotqa
# Data Indices: [1382, 1859, 3833, 892, 1853]

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
        It uses FlexibleCustom with structured reasoning steps to break down complex problems.
        """
        # Step 1: Use FlexibleCustom for structured multi-hop reasoning
        solution = await self.flexible_custom(
            custom_instruction="Break the problem into smaller steps and reason through each step logically.",
            reasoning_pattern="sequential",
            steps=["extract_entities", "find_connections", "trace_reasoning_path", "synthesize_answer"]
        )

        # Step 2: Optionally refine using Review if needed (e.g., for complex problems)
        refined_solution = await self.review(pre_solution=solution)

        # Step 3: Ensemble with a direct answer for robustness
        direct_answer = await self.answer_generate()
        ensemble = await self.sc_ensemble(solutions=[refined_solution, direct_answer])

        return ensemble