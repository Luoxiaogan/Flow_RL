# Workflow ID: hotpotqa_646_0
# Benchmark: hotpotqa
# Data Indices: [1243, 537, 3561, 1571]

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
        It breaks down the problem step-by-step and synthesizes an answer through structured multi-hop reasoning.
        """
        # Step 1: Use FlexibleCustom to perform sequential multi-hop reasoning
        solution = await self.flexible_custom(
            custom_instruction="Break down the problem into logical steps and trace connections between pieces of information.",
            reasoning_pattern="sequential",
            steps=["identify_key_entities", "find_intermediate_connections", "trace_reasoning_path", "synthesize_final_answer"]
        )

        # Step 2: Generate a direct answer as a baseline for ensemble
        baseline_answer = await self.answer_generate()

        # Step 3: Review the flexible custom solution to refine it
        refined_solution = await self.review(pre_solution=solution)

        # Step 4: Ensemble the baseline and refined solutions for improved accuracy
        final_solution = await self.sc_ensemble(solutions=[baseline_answer, refined_solution])

        return final_solution