# Workflow ID: hotpotqa_208_0
# Benchmark: hotpotqa
# Data Indices: [3103, 756, 1465, 2324]

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
        # Step 1: Generate initial answer directly
        direct_answer = await self.answer_generate()

        # Step 2: Use flexible custom with sequential reasoning for structured multi-hop thinking
        multi_hop_solution = await self.flexible_custom(
            custom_instruction="Break down the problem step by step, connecting relevant pieces of information logically.",
            reasoning_pattern="sequential",
            steps=["identify_key_entities", "find_intermediate_connections", "trace_reasoning_path", "synthesize_final_answer"]
        )

        # Step 3: Generate alternative reasoning via Custom with step-by-step instruction
        step_by_step_solution = await self.custom(
            instruction="Can you solve this problem by breaking it down into detailed steps and explaining the reasoning behind each step?"
        )

        # Step 4: Ensemble the three solutions to select the best one
        solutions = [direct_answer, multi_hop_solution, step_by_step_solution]
        ensembled_answer = await self.sc_ensemble(solutions=solutions)

        # Step 5: Final review to refine the ensembled solution
        final_answer = await self.review(pre_solution=ensembled_answer)

        return final_answer