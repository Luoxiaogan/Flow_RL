# Workflow ID: hotpotqa_575_0
# Benchmark: hotpotqa
# Data Indices: [3536, 3787, 3191, 356]

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
        It uses multiple reasoning paths and ensemble to improve accuracy.
        """
        # Step 1: Generate initial answer using direct generation
        direct_answer = await self.answer_generate()

        # Step 2: Use flexible custom with sequential reasoning for structured multi-hop thinking
        multi_hop_reasoning = await self.flexible_custom(
            custom_instruction="Break down the problem into smaller steps and explain each reasoning step clearly.",
            reasoning_pattern="sequential",
            steps=["identify_key_entities", "find_intermediate_connections", "trace_logical_path", "synthesize_final_answer"]
        )

        # Step 3: Generate alternative reasoning via Custom with step-by-step instruction
        step_by_step_solution = await self.custom(
            instruction="Solve this by breaking it down into detailed steps and explaining the reasoning behind each step."
        )

        # Step 4: Ensemble all solutions to select the best one
        solutions = [direct_answer, multi_hop_reasoning, step_by_step_solution]
        ensembled_answer = await self.sc_ensemble(solutions=solutions)

        # Step 5: Final review to refine the selected solution
        final_answer = await self.review(pre_solution=ensembled_answer)

        return final_answer