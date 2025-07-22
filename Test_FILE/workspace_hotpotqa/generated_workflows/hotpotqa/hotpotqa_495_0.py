# Workflow ID: hotpotqa_495_0
# Benchmark: hotpotqa
# Data Indices: [2107, 3100, 2124, 2110, 1979]

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
        It uses FlexibleCustom with sequential reasoning to break down the problem,
        then optionally reviews and ensembles solutions for robustness.
        """
        # Step 1: Use FlexibleCustom for structured multi-hop reasoning
        solution = await self.flexible_custom(
            custom_instruction="Break down the problem into key entities and connections step-by-step.",
            reasoning_pattern="sequential",
            steps=["extract_entities", "find_connections", "trace_reasoning_path", "synthesize_answer"]
        )

        # Step 2: Optionally refine with review if needed
        refined_solution = await self.review(pre_solution=solution)

        # Step 3: Ensemble with direct answer generation for robustness
        direct_answer = await self.answer_generate()
        ensemble_solution = await self.sc_ensemble(solutions=[refined_solution, direct_answer])

        return ensemble_solution