# Workflow ID: hotpotqa_233_0
# Benchmark: hotpotqa
# Data Indices: [2642, 3680, 2380, 665]

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
        This is a workflow graph for multi-hop question answering using sequential reasoning.
        It traces connections step-by-step through the context to solve complex problems.
        """
        # Step 1: Use FlexibleCustom with sequential pattern to trace multi-hop connections
        solution = await self.flexible_custom(
            custom_instruction="Break down the problem into logical steps and trace connections between pieces of information sequentially.",
            reasoning_pattern="sequential",
            steps=["identify_key_entities", "find intermediate connections", "trace reasoning path", "synthesize final answer"]
        )

        # Step 2: Review the initial solution to improve accuracy
        reviewed_solution = await self.review(pre_solution=solution)

        # Step 3: Generate an alternative direct answer for ensemble
        direct_answer = await self.answer_generate()

        # Step 4: Ensemble the two solutions to select the best one
        final_answer = await self.sc_ensemble(solutions=[reviewed_solution, direct_answer])

        return final_answer