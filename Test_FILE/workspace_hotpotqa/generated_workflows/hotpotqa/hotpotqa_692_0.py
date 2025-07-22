# Workflow ID: hotpotqa_692_0
# Benchmark: hotpotqa
# Data Indices: [2519, 1274, 211, 1232, 1830]

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
        This is a workflow graph for multi-hop question answering using sequential reasoning.
        It first breaks down the problem step-by-step, then generates an answer, reviews it, and finally ensembles with alternatives.
        """
        # Step 1: Use FlexibleCustom to trace multi-hop connections sequentially
        solution = await self.flexible_custom(
            custom_instruction="Break down the problem into smaller steps and reason through each step logically.",
            reasoning_pattern="sequential",
            steps=["identify_key_entities", "find_intermediate_connections", "trace_reasoning_path", "synthesize_final_answer"]
        )

        # Step 2: Generate a direct answer as a baseline
        direct_answer = await self.answer_generate()

        # Step 3: Review the initial solution to refine it
        reviewed_solution = await self.review(pre_solution=solution)

        # Step 4: Ensemble multiple solutions (original + reviewed + direct) to improve accuracy
        ensemble_input = [solution, reviewed_solution, direct_answer]
        final_answer = await self.sc_ensemble(solutions=ensemble_input)

        return final_answer