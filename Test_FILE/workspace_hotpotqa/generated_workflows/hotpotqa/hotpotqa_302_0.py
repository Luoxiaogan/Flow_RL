# Workflow ID: hotpotqa_302_0
# Benchmark: hotpotqa
# Data Indices: [2185, 2496, 1832, 1424, 3230]

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
        # Step 1: Use FlexibleCustom with sequential reasoning to trace connections step-by-step
        solution_1 = await self.flexible_custom(
            custom_instruction="Break down the problem into smaller steps and explain the reasoning behind each step.",
            reasoning_pattern="sequential",
            steps=["identify_key_entities", "find_intermediate_connections", "trace_reasoning_path", "synthesize_final_answer"]
        )

        # Step 2: Generate a direct answer for comparison
        solution_2 = await self.answer_generate()

        # Step 3: Review the first solution to refine it
        reviewed_solution = await self.review(pre_solution=solution_1)

        # Step 4: Ensemble the solutions from direct generation and refined solution
        ensemble_solution = await self.sc_ensemble(solutions=[solution_2, reviewed_solution])

        return ensemble_solution