# Workflow ID: hotpotqa_173_0
# Benchmark: hotpotqa
# Data Indices: [2202, 3736, 3675, 3507, 1351]

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
        It uses multiple reasoning paths to enhance robustness and selects the best answer via ensemble.
        """
        # Step 1: Generate initial answer using direct reasoning
        direct_answer = await self.answer_generate()

        # Step 2: Use Custom to break down the problem into steps
        step_by_step_reasoning = await self.custom(
            instruction="Can you solve this problem by breaking it down into detailed steps and explaining the reasoning behind each step?"
        )

        # Step 3: Use FlexibleCustom with sequential reasoning for multi-hop logic
        multi_hop_reasoning = await self.flexible_custom(
            custom_instruction="Focus on connecting information across different parts of the context",
            reasoning_pattern="sequential",
            steps=["identify_entities", "find_connections", "trace_reasoning_path", "synthesize_answer"]
        )

        # Step 4: Collect all solutions for ensemble
        solutions = [direct_answer, step_by_step_reasoning, multi_hop_reasoning]

        # Step 5: Ensemble the solutions to select the most reliable one
        ensembled_answer = await self.sc_ensemble(solutions=solutions)

        # Step 6: Final review to refine the selected solution
        final_answer = await self.review(pre_solution=ensembled_answer)

        return final_answer