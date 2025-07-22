# Workflow ID: hotpotqa_26_0
# Benchmark: hotpotqa
# Data Indices: [1613, 3117, 3537, 3455]

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
        This is a robust workflow graph for multi-hop question answering.
        It uses multiple reasoning paths and ensembles the best solution.
        """
        # Step 1: Generate initial answer using direct generation
        direct_answer = await self.answer_generate()

        # Step 2: Generate answer using step-by-step breakdown (custom)
        step_by_step_answer = await self.custom(instruction="Can you solve this problem by breaking it down into detailed steps and explaining the reasoning behind each step?")

        # Step 3: Use flexible custom with sequential reasoning to trace multi-hop connections
        multi_hop_answer = await self.flexible_custom(
            custom_instruction="Focus on connecting information across different parts of the context",
            reasoning_pattern="sequential",
            steps=["identify_entities", "find_connections", "trace_reasoning_path", "synthesize_answer"]
        )

        # Step 4: Ensemble the three solutions to select the best one
        ensemble_solution = await self.sc_ensemble(solutions=[direct_answer, step_by_step_answer, multi_hop_answer])

        # Step 5: Final review to refine and verify the selected solution
        final_answer = await self.review(pre_solution=ensemble_solution)

        return final_answer