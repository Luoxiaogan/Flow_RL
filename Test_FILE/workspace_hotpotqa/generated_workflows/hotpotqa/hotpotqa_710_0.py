# Workflow ID: hotpotqa_710_0
# Benchmark: hotpotqa
# Data Indices: [1991, 1456, 1818, 283]

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

        # Step 2: Use flexible custom to explore multi-hop reasoning via sequential steps
        multi_hop_solution = await self.flexible_custom(
            custom_instruction="Break down the problem into smaller steps and reason through each step sequentially.",
            reasoning_pattern="sequential",
            steps=["identify_key_entities", "find_intermediate_connections", "trace_reasoning_path", "synthesize_final_answer"]
        )

        # Step 3: Generate alternative reasoning path using Custom with detailed step-by-step instruction
        step_by_step_solution = await self.custom(
            instruction="Solve this problem by breaking it down into detailed steps and explaining the reasoning behind each step."
        )

        # Step 4: Ensemble the three solutions to select the most robust answer
        ensemble_candidates = [direct_answer, multi_hop_solution, step_by_step_solution]
        final_answer = await self.sc_ensemble(solutions=ensemble_candidates)

        # Step 5: Final review to refine the selected answer
        refined_answer = await self.review(pre_solution=final_answer)

        return refined_answer