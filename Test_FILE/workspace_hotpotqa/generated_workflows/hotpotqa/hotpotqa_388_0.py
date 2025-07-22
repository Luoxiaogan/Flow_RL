# Workflow ID: hotpotqa_388_0
# Benchmark: hotpotqa
# Data Indices: [1796, 3225, 2075, 227]

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
        It breaks down the problem step-by-step to trace connections across multiple pieces of context.
        """
        # Step 1: Use FlexibleCustom with sequential reasoning to trace multi-hop connections
        solution = await self.flexible_custom(
            custom_instruction="Break down the problem into smaller steps and explain the reasoning behind each step.",
            reasoning_pattern="sequential",
            steps=["identify_key_entities", "find_intermediate_connections", "trace_reasoning_path", "synthesize_final_answer"]
        )

        # Step 2: Generate an answer based on the structured reasoning
        answer = await self.answer_generate()

        # Step 3: Review the generated answer to improve accuracy
        reviewed_answer = await self.review(pre_solution=answer)

        # Step 4: Ensemble the original solution (from flexible_custom) and the reviewed answer
        ensemble_solution = await self.sc_ensemble(solutions=[solution, reviewed_answer])

        return ensemble_solution