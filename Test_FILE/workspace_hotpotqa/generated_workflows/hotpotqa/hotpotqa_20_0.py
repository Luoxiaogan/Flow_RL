# Workflow ID: hotpotqa_20_0
# Benchmark: hotpotqa
# Data Indices: [2916, 432, 694, 114, 1634]

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
        It uses FlexibleCustom for sequential reasoning to extract and connect facts,
        then Custom to synthesize the answer, followed by Review for validation.
        Finally, it ensembles multiple solutions for robustness.
        """
        # Step 1: Use FlexibleCustom with sequential reasoning to break down and trace connections
        solution_step1 = await self.flexible_custom(
            custom_instruction="Break down the problem step-by-step, identifying key entities and connecting them logically.",
            reasoning_pattern="sequential",
            steps=["identify_key_entities", "find_intermediate_connections", "trace_reasoning_path", "synthesize_answer"]
        )

        # Step 2: Generate a direct answer using Custom (step-by-step thinking encouraged)
        solution_step2 = await self.custom(instruction="Solve this problem by breaking it down into detailed steps and explaining the reasoning behind each step.")

        # Step 3: Generate another independent solution via Custom for diversity
        solution_step3 = await self.custom(instruction="Explain how to solve the problem with clear reasoning for each step.")

        # Step 4: Ensemble the three solutions to select the best one
        ensemble_solutions = [solution_step1, solution_step2, solution_step3]
        final_solution = await self.sc_ensemble(solutions=ensemble_solutions)

        # Step 5: Review the final solution for correctness and clarity
        reviewed_solution = await self.review(pre_solution=final_solution)

        return reviewed_solution