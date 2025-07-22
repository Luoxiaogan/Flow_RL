# Workflow ID: hotpotqa_544_0
# Benchmark: hotpotqa
# Data Indices: [2757, 334, 111, 1313]

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
        It breaks down the problem into steps, traces connections across context, and refines the answer.
        """
        # Step 1: Use flexible custom to perform step-by-step reasoning (sequential multi-hop)
        solution = await self.flexible_custom(
            custom_instruction="Break down the problem into smaller steps and explain each reasoning step clearly.",
            reasoning_pattern="sequential",
            steps=["identify_key_entities", "find_intermediate_connections", "trace_reasoning_path", "synthesize_final_answer"]
        )

        # Step 2: Review the generated solution to refine it
        reviewed_solution = await self.review(pre_solution=solution)

        # Step 3: Generate a direct answer as a baseline for ensemble
        direct_answer = await self.answer_generate()

        # Step 4: Ensemble the reviewed solution and direct answer to improve robustness
        final_solution = await self.sc_ensemble(solutions=[reviewed_solution, direct_answer])

        return final_solution