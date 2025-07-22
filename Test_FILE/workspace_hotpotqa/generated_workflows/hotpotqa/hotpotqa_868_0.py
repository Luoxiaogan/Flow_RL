# Workflow ID: hotpotqa_868_0
# Benchmark: hotpotqa
# Data Indices: [3917, 2600, 355, 2689]

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
        It breaks down the problem step-by-step and traces connections across information sources.
        """
        # Step 1: Use FlexibleCustom with sequential reasoning to trace multi-hop connections
        solution = await self.flexible_custom(
            custom_instruction="Break down the problem into smaller steps and explain the reasoning behind each step.",
            reasoning_pattern="sequential",
            steps=["identify_key_entities", "find_intermediate_connections", "trace_reasoning_path", "synthesize_final_answer"]
        )

        # Step 2: Generate an answer based on the structured reasoning
        answer = await self.answer_generate()

        # Step 3: Review the initial answer to improve accuracy
        reviewed_answer = await self.review(pre_solution=answer)

        # Step 4: Ensemble multiple solutions (generate two different answers via Custom for diversity)
        diverse_solution_1 = await self.custom(instruction="Solve this problem by breaking it down into detailed steps and explaining the reasoning behind each step.")
        diverse_solution_2 = await self.custom(instruction="Explain how to solve the problem with clear reasoning for each step.")
        ensemble_result = await self.sc_ensemble(solutions=[solution, reviewed_answer, diverse_solution_1, diverse_solution_2])

        return ensemble_result