# Workflow ID: hotpotqa_531_0
# Benchmark: hotpotqa
# Data Indices: [695, 3345, 1485, 1768]

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
        It breaks down the problem into steps, traces connections across sources, and refines the answer.
        """
        # Step 1: Use FlexibleCustom with sequential multi-hop pattern to trace information step-by-step
        solution = await self.flexible_custom(
            custom_instruction="Break down the problem into smaller steps and reason through each connection sequentially.",
            reasoning_pattern="sequential",
            steps=["identify_key_entities", "find_intermediate_connections", "trace_reasoning_path", "synthesize_final_answer"]
        )

        # Step 2: Review the initial solution to refine it based on internal consistency
        reviewed_solution = await self.review(pre_solution=solution)

        # Step 3: Generate an answer directly as a baseline for ensemble
        direct_answer = await self.answer_generate()

        # Step 4: Ensemble the reviewed solution and direct answer to improve robustness
        final_solution = await self.sc_ensemble(solutions=[reviewed_solution, direct_answer])

        return final_solution