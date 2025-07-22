# Workflow ID: hotpotqa_319_0
# Benchmark: hotpotqa
# Data Indices: [520, 572, 1162, 2164, 1115]

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

        # Step 2: Generate step-by-step reasoning using Custom with detailed instruction
        step_by_step = await self.custom(instruction="Can you solve this problem by breaking it down into detailed steps and explaining the reasoning behind each step?")

        # Step 3: Use FlexibleCustom to explore a structured multi-hop path
        multi_hop_reasoning = await self.flexible_custom(
            custom_instruction="Focus on connecting information across different parts of the context",
            reasoning_pattern="sequential",
            steps=["identify_entities", "find_connections", "trace_reasoning_path", "synthesize_answer"]
        )

        # Step 4: Ensemble all three solutions to select the most well-supported one
        solutions = [direct_answer, step_by_step, multi_hop_reasoning]
        ensembled_solution = await self.sc_ensemble(solutions=solutions)

        # Step 5: Final review to refine the selected solution
        final_answer = await self.review(pre_solution=ensembled_solution)

        return final_answer