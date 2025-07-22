# Workflow ID: hotpotqa_709_0
# Benchmark: hotpotqa
# Data Indices: [408, 768, 3464, 1349]

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
        It uses FlexibleCustom with sequential reasoning to break down the problem,
        then generates an answer, reviews it, and ensembles with alternatives for robustness.
        """
        # Step 1: Use flexible custom to extract entities and trace connections step-by-step
        solution_1 = await self.flexible_custom(
            custom_instruction="Break down the problem into smaller steps and explain reasoning for each step.",
            reasoning_pattern="sequential",
            steps=["extract_entities", "find_connections", "trace_reasoning_path", "synthesize_answer"]
        )

        # Step 2: Generate a direct answer using AnswerGenerate
        solution_2 = await self.answer_generate()

        # Step 3: Review the first solution to refine it
        reviewed_solution = await self.review(pre_solution=solution_1)

        # Step 4: Ensemble multiple solutions (including original and reviewed) for final output
        ensemble_solutions = [solution_1, solution_2, reviewed_solution]
        final_answer = await self.sc_ensemble(solutions=ensemble_solutions)

        return final_answer