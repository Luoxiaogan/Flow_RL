# Workflow ID: hotpotqa_434_0
# Benchmark: hotpotqa
# Data Indices: [625, 3298, 233, 1325, 3212]

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
        Uses FlexibleCustom for structured multi-hop reasoning and ensembles solutions for robustness.
        """
        # Step 1: Use flexible custom to break down the problem with structured reasoning
        solution_1 = await self.flexible_custom(
            custom_instruction="Break down the problem into key entities, connections, and logical steps to solve it.",
            reasoning_pattern="sequential",
            steps=["extract_entities", "find_connections", "trace_reasoning_path", "synthesize_answer"]
        )

        # Step 2: Generate a direct answer using AnswerGenerate for baseline
        solution_2 = await self.answer_generate()

        # Step 3: Review the direct answer to refine it
        refined_solution = await self.review(pre_solution=solution_2)

        # Step 4: Ensemble both the structured and refined answers
        ensemble_solution = await self.sc_ensemble(solutions=[solution_1, refined_solution])

        return ensemble_solution