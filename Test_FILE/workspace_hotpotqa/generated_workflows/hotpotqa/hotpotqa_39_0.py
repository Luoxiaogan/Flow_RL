# Workflow ID: hotpotqa_39_0
# Benchmark: hotpotqa
# Data Indices: [3391, 1950, 3510, 242, 3257]

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
        It breaks down the problem into steps, traces connections, and refines the answer.
        """
        # Step 1: Use FlexibleCustom to break down the problem sequentially
        solution_step1 = await self.flexible_custom(
            custom_instruction="Break down the problem step by step, identifying key entities and relationships.",
            reasoning_pattern="sequential",
            steps=["identify_key_entities", "find_intermediate_connections", "trace_reasoning_path", "synthesize_final_answer"]
        )

        # Step 2: Generate an initial answer based on the structured breakdown
        solution_step2 = await self.answer_generate()

        # Step 3: Review the initial answer to refine it
        refined_solution = await self.review(pre_solution=solution_step2)

        # Step 4: Ensemble multiple solutions (e.g., from different reasoning paths)
        solutions_list = [solution_step1, refined_solution]
        ensembled_solution = await self.sc_ensemble(solutions=solutions_list)

        return ensembled_solution