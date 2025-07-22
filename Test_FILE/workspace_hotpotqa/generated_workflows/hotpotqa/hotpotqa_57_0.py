# Workflow ID: hotpotqa_57_0
# Benchmark: hotpotqa
# Data Indices: [2848, 1, 2235, 2799]

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
        It uses flexible custom for step-by-step reasoning, custom for synthesis, and review for validation.
        """
        # Step 1: Use FlexibleCustom with sequential reasoning to extract and connect facts
        solution_1 = await self.flexible_custom(
            custom_instruction="Break down the problem into smaller steps and trace connections between pieces of information.",
            reasoning_pattern="sequential",
            steps=["identify_key_entities", "find_intermediate_connections", "trace_reasoning_path", "synthesize_answer"]
        )

        # Step 2: Use Custom to synthesize a coherent answer based on extracted facts
        solution_2 = await self.custom(instruction="Solve this by breaking it down into detailed steps and explaining the reasoning behind each step.")

        # Step 3: Ensemble both solutions to improve accuracy
        ensemble_solution = await self.sc_ensemble(solutions=[solution_1, solution_2])

        # Step 4: Review the ensembled solution to refine and validate
        final_solution = await self.review(pre_solution=ensemble_solution)

        return final_solution