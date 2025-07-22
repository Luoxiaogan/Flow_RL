# Workflow ID: hotpotqa_284_0
# Benchmark: hotpotqa
# Data Indices: [2583, 3818, 2085, 27]

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
        It uses flexible custom reasoning to break down the problem into key steps: 
        extract_entities, find_connections, and synthesize_answer.
        """
        # Step 1: Use FlexibleCustom for structured multi-hop reasoning
        solution = await self.flexible_custom(
            custom_instruction="Break down the problem step by step using entity extraction, connection finding, and synthesis.",
            reasoning_pattern="sequential",
            steps=["extract_entities", "find_connections", "synthesize_answer"]
        )

        # Step 2: Optionally refine with review if needed
        refined_solution = await self.review(pre_solution=solution)

        # Step 3: Ensemble with direct answer generation as a fallback
        direct_answer = await self.answer_generate()
        ensemble_solution = await self.sc_ensemble(solutions=[refined_solution, direct_answer])

        return ensemble_solution