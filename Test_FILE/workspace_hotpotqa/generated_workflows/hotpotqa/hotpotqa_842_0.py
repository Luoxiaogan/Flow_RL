# Workflow ID: hotpotqa_842_0
# Benchmark: hotpotqa
# Data Indices: [2875, 3227, 1436, 3580, 1333]

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
        then optionally refines the solution via review, and finally ensembles multiple attempts.
        """
        # Step 1: Use flexible custom for structured multi-hop reasoning
        solution = await self.flexible_custom(
            custom_instruction="Break down the problem into smaller steps by extracting key entities, finding connections between them, and synthesizing an answer.",
            reasoning_pattern="sequential",
            steps=["extract_entities", "find_connections", "synthesize_answer"]
        )

        # Step 2: Optionally refine using Review if the initial solution lacks clarity or completeness
        refined_solution = await self.review(pre_solution=solution)

        # Step 3: Generate a direct answer as a baseline for ensemble
        direct_answer = await self.answer_generate()

        # Step 4: Ensemble the original and refined solutions to improve robustness
        final_solution = await self.sc_ensemble(solutions=[solution, refined_solution, direct_answer])

        return final_solution