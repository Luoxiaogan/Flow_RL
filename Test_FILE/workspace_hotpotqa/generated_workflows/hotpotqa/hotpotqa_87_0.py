# Workflow ID: hotpotqa_87_0
# Benchmark: hotpotqa
# Data Indices: [457, 1682, 3418, 3494]

class Workflow:
    def __init__(
        self,
        config,
        problem
    ) -> None:
        self.problem = problem
        self.config = create(config)
        self.flexible_custom = operator.FlexibleCustom(self.config, self.problem)
        self.custom = operator.Custom(self.config, self.problem)
        self.sc_ensemble = operator.ScEnsemble(self.config, self.problem)
        self.review = operator.Review(self.config, self.problem)

    async def run_workflow(self):
        """
        This is a workflow graph for multi-hop question answering.
        It uses FlexibleCustom for step-by-step reasoning, Custom for synthesis, 
        and Review for validation to ensure robust answer generation.
        """
        # Step 1: Use FlexibleCustom with sequential reasoning to extract and connect facts
        solution_1 = await self.flexible_custom(
            custom_instruction="Break down the problem into smaller steps and explain the reasoning behind each step.",
            reasoning_pattern="sequential",
            steps=["identify_key_entities", "find_intermediate_connections", "trace_reasoning_path", "synthesize_answer"]
        )

        # Step 2: Generate an initial answer using Custom with detailed reasoning
        solution_2 = await self.custom(
            instruction="Solve this problem by breaking it down into detailed steps and explaining the reasoning behind each step."
        )

        # Step 3: Ensemble the two solutions to improve accuracy
        solutions = [solution_1, solution_2]
        ensembled_solution = await self.sc_ensemble(solutions=solutions)

        # Step 4: Review the ensembled solution to refine and validate
        final_answer = await self.review(pre_solution=ensembled_solution)

        return final_answer