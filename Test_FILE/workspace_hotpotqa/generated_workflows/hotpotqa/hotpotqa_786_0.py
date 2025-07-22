# Workflow ID: hotpotqa_786_0
# Benchmark: hotpotqa
# Data Indices: [1461, 131, 3662, 2904, 746]

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
        It uses flexible custom reasoning to break down the problem step-by-step,
        then refines the answer through review and ensembles multiple solutions.
        """
        # Step 1: Use FlexibleCustom with sequential reasoning to trace multi-hop connections
        solution = await self.flexible_custom(
            custom_instruction="Break down the problem into smaller steps and explain each reasoning step clearly.",
            reasoning_pattern="sequential",
            steps=["extract_entities", "find_connections", "trace_reasoning_path", "synthesize_answer"]
        )

        # Step 2: Review the generated solution to improve accuracy
        reviewed_solution = await self.review(pre_solution=solution)

        # Step 3: Generate an alternative direct answer for ensemble
        direct_answer = await self.answer_generate()

        # Step 4: Ensemble both solutions to select the best one
        final_answer = await self.sc_ensemble(solutions=[reviewed_solution, direct_answer])

        return final_answer