# Workflow ID: hotpotqa_758_0
# Benchmark: hotpotqa
# Data Indices: [3704, 46, 2572, 1340, 310]

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
        """
        # Step 1: Use FlexibleCustom to trace multi-hop connections sequentially
        solution1 = await self.flexible_custom(
            custom_instruction="Break down the problem into smaller steps and trace the reasoning path step-by-step.",
            reasoning_pattern="sequential",
            steps=["identify_key_entities", "find_intermediate_connections", "trace_reasoning_path", "synthesize_final_answer"]
        )

        # Step 2: Generate an independent answer directly
        solution2 = await self.answer_generate()

        # Step 3: Review the initial solution to refine it
        refined_solution = await self.review(pre_solution=solution1)

        # Step 4: Ensemble the two solutions (original flexible custom + refined) to improve accuracy
        ensemble_solution = await self.sc_ensemble(solutions=[solution1, refined_solution])

        return ensemble_solution