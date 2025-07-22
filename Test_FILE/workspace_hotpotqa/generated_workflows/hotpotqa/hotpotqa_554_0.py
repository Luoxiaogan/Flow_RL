# Workflow ID: hotpotqa_554_0
# Benchmark: hotpotqa
# Data Indices: [3743, 3919, 716, 165]

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
        # Step 1: Generate initial answer using direct reasoning
        direct_answer = await self.answer_generate()

        # Step 2: Generate step-by-step breakdown of the problem
        step_by_step = await self.custom(instruction="Can you solve this problem by breaking it down into detailed steps and explaining the reasoning behind each step?")

        # Step 3: Use flexible custom with sequential reasoning for structured multi-hop thinking
        multi_hop_reasoning = await self.flexible_custom(
            custom_instruction="Focus on connecting information across different parts of the context",
            reasoning_pattern="sequential",
            steps=["identify_entities", "find_connections", "trace_reasoning_path", "synthesize_answer"]
        )

        # Step 4: Ensemble the three solutions to select the best one
        solutions = [direct_answer, step_by_step, multi_hop_reasoning]
        ensembled_solution = await self.sc_ensemble(solutions=solutions)

        # Step 5: Final review to refine the ensembled solution
        final_answer = await self.review(pre_solution=ensembled_solution)

        return final_answer