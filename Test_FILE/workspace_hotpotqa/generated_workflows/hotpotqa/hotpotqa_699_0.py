# Workflow ID: hotpotqa_699_0
# Benchmark: hotpotqa
# Data Indices: [502, 3409, 1267, 2227]

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
        # Step 1: Use FlexibleCustom to trace connections step-by-step through the context
        solution_1 = await self.flexible_custom(
            custom_instruction="Focus on connecting information across different parts of the context",
            reasoning_pattern="sequential",
            steps=["identify_entities", "find_connections", "trace_reasoning_path", "synthesize_answer"]
        )

        # Step 2: Generate an initial answer directly
        solution_2 = await self.answer_generate()

        # Step 3: Review the initial answer to refine it
        solution_3 = await self.review(pre_solution=solution_2)

        # Step 4: Ensemble the two solutions (from flexible_custom and review) to get the best one
        ensemble_solution = await self.sc_ensemble(solutions=[solution_1, solution_3])

        return ensemble_solution