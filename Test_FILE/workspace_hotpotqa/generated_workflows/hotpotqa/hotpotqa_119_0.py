# Workflow ID: hotpotqa_119_0
# Benchmark: hotpotqa
# Data Indices: [421, 3781, 3713, 3776]

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
        # Step 1: Generate initial answer using direct reasoning
        direct_answer = await self.answer_generate()

        # Step 2: Use Custom to break down the problem into steps
        step_by_step = await self.custom(instruction="Can you solve this problem by breaking it down into detailed steps and explaining the reasoning behind each step?")

        # Step 3: Use FlexibleCustom for structured multi-hop reasoning (sequential)
        multi_hop_solution = await self.flexible_custom(
            custom_instruction="Focus on connecting information across different parts of the context",
            reasoning_pattern="sequential",
            steps=["identify_entities", "find_connections", "trace_reasoning_path", "synthesize_answer"]
        )

        # Step 4: Ensemble the three solutions to get the most robust answer
        solutions = [direct_answer, step_by_step, multi_hop_solution]
        ensemble_answer = await self.sc_ensemble(solutions=solutions)

        # Step 5: Final review to refine the ensemble result
        final_answer = await self.review(pre_solution=ensemble_answer)

        return final_answer