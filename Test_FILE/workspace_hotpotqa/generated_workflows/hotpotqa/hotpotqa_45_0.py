# Workflow ID: hotpotqa_45_0
# Benchmark: hotpotqa
# Data Indices: [524, 3498, 2348, 3683]

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
        It uses multiple reasoning paths and ensembles the best solution.
        """
        # Step 1: Generate initial answer using direct generation
        direct_answer = await self.answer_generate()

        # Step 2: Generate reasoning-based answer using custom instruction (step-by-step breakdown)
        step_by_step_answer = await self.custom(instruction="Can you solve this problem by breaking it down into detailed steps and explaining the reasoning behind each step?")

        # Step 3: Use flexible custom to explore multi-hop reasoning via sequential path
        multi_hop_answer = await self.flexible_custom(
            custom_instruction="Focus on connecting information across different parts of the context",
            reasoning_pattern="sequential",
            steps=["identify_entities", "find_connections", "trace_reasoning_path", "synthesize_answer"]
        )

        # Step 4: Ensemble the three solutions to select the best one
        ensemble_solution = await self.sc_ensemble(solutions=[direct_answer, step_by_step_answer, multi_hop_answer])

        # Step 5: Final review to refine the selected solution
        final_answer = await self.review(pre_solution=ensemble_solution)

        return final_answer