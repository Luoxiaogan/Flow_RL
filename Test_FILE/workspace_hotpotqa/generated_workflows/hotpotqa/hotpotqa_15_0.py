# Workflow ID: hotpotqa_15_0
# Benchmark: hotpotqa
# Data Indices: [3144, 1669, 2542, 47]

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
            custom_instruction="Break the problem into key entities, find connections between them, and synthesize a clear answer.",
            reasoning_pattern="sequential",
            steps=["extract_entities", "find_connections", "synthesize_answer"]
        )

        # Step 2: Optionally review the generated solution for refinement
        reviewed_solution = await self.review(pre_solution=solution)

        # Step 3: Generate final answer using direct generation as a fallback or confirmation
        final_answer = await self.answer_generate()

        # Step 4: Ensemble the initial solution and the reviewed one for robustness
        ensemble_solution = await self.sc_ensemble(solutions=[solution, reviewed_solution])

        return ensemble_solution