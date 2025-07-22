# Workflow ID: hotpotqa_792_0
# Benchmark: hotpotqa
# Data Indices: [1803, 826, 2373, 870]

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
        It uses multiple reasoning paths and ensemble to improve robustness.
        """
        # Step 1: Generate initial answer directly (baseline)
        direct_answer = await self.answer_generate()

        # Step 2: Use flexible custom to explore structured multi-hop reasoning
        multi_hop_solution = await self.flexible_custom(
            custom_instruction="Break down the problem into smaller steps and reason through each logically.",
            reasoning_pattern="sequential",
            steps=["identify_key_entities", "find_intermediate_connections", "trace_reasoning_path", "synthesize_final_answer"]
        )

        # Step 3: Use Custom with step-by-step instruction to generate another reasoning path
        step_by_step_solution = await self.custom(
            instruction="Solve this problem by breaking it down into detailed steps and explaining the reasoning behind each step."
        )

        # Step 4: Ensemble the three solutions to select the best one
        solutions = [direct_answer, multi_hop_solution, step_by_step_solution]
        ensembled_answer = await self.sc_ensemble(solutions=solutions)

        # Step 5: Final review to refine the selected answer
        final_answer = await self.review(pre_solution=ensembled_answer)

        return final_answer