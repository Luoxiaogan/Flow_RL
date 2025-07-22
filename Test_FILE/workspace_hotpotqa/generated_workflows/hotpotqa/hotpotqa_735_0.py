# Workflow ID: hotpotqa_735_0
# Benchmark: hotpotqa
# Data Indices: [2586, 3961, 1098, 2431, 328]

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
        It breaks down the problem into smaller steps and traces connections across context.
        """
        # Step 1: Use flexible custom to break down the problem sequentially
        solution_step1 = await self.flexible_custom(
            custom_instruction="Break down the problem into smaller, logical steps and explain each step in detail.",
            reasoning_pattern="sequential",
            steps=["identify_key_entities", "find_intermediate_connections", "trace_reasoning_path", "synthesize_final_answer"]
        )

        # Step 2: Generate an initial answer based on the structured reasoning
        solution_step2 = await self.answer_generate()

        # Step 3: Review the generated answer using the structured reasoning as context
        reviewed_solution = await self.review(pre_solution=solution_step2)

        # Step 4: Ensemble multiple solutions (one from direct generation, one from review)
        ensemble_solution = await self.sc_ensemble(solutions=[solution_step2, reviewed_solution])

        return ensemble_solution