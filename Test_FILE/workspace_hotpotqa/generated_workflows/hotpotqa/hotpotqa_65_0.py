# Workflow ID: hotpotqa_65_0
# Benchmark: hotpotqa
# Data Indices: [2941, 1370, 1009, 2783]

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
        It uses multiple reasoning paths to enhance robustness and ensembles the best solution.
        """
        # Step 1: Generate initial answer using direct generation
        direct_answer = await self.answer_generate()

        # Step 2: Use flexible custom to explore multi-hop reasoning via sequential steps
        multi_hop_solution = await self.flexible_custom(
            custom_instruction="Break down the problem into smaller steps and trace connections between them.",
            reasoning_pattern="sequential",
            steps=["identify_key_entities", "find_intermediate_connections", "trace_reasoning_path", "synthesize_final_answer"]
        )

        # Step 3: Generate alternative reasoning path using Custom with step-by-step instruction
        step_by_step_solution = await self.custom(
            instruction="Solve this by breaking it down into detailed steps and explaining the reasoning behind each step."
        )

        # Step 4: Ensemble the three solutions to select the most consistent and well-supported answer
        ensemble_input = [direct_answer, multi_hop_solution, step_by_step_solution]
        final_answer = await self.sc_ensemble(solutions=ensemble_input)

        # Step 5: Final review to refine and verify the selected answer
        reviewed_answer = await self.review(pre_solution=final_answer)

        return reviewed_answer