# Workflow ID: hotpotqa_190_0
# Benchmark: hotpotqa
# Data Indices: [3449, 3371, 3989, 2681]

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
        then refines the solution through review and ensembles multiple solutions.
        """
        # Step 1: Use flexible custom to extract entities, find connections, and synthesize answer
        solution = await self.flexible_custom(
            custom_instruction="Break down the problem step by step, identify key entities, find connections between them, and synthesize the final answer.",
            reasoning_pattern="sequential",
            steps=["extract_entities", "find_connections", "synthesize_answer"]
        )

        # Step 2: Generate an alternative direct answer for ensemble
        direct_answer = await self.answer_generate()

        # Step 3: Review the initial solution to refine it
        refined_solution = await self.review(pre_solution=solution)

        # Step 4: Ensemble the direct answer and refined solution to improve accuracy
        final_answer = await self.sc_ensemble(solutions=[direct_answer, refined_solution])

        return final_answer