# Workflow ID: hotpotqa_462_0
# Benchmark: hotpotqa
# Data Indices: [697, 1242, 2672, 2271, 2028]

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
        It uses flexible custom for sequential reasoning to extract and connect facts,
        then synthesizes the solution with a custom agent, validates with review,
        and finally ensembles multiple solutions for robustness.
        """
        # Step 1: Use FlexibleCustom with sequential reasoning to break down and trace the multi-hop path
        reasoning_solution = await self.flexible_custom(
            custom_instruction="Break down the problem into smaller steps and explain the reasoning behind each step.",
            reasoning_pattern="sequential",
            steps=["identify_key_entities", "find_intermediate_connections", "trace_reasoning_path", "synthesize_answer"]
        )

        # Step 2: Use Custom to synthesize a clear, concise answer based on the structured reasoning
        synthesized_answer = await self.custom(instruction="Based on the detailed reasoning above, generate a final answer that directly addresses the question.")

        # Step 3: Review the synthesized answer to ensure accuracy and clarity
        reviewed_answer = await self.review(pre_solution=synthesized_answer)

        # Step 4: Generate alternative solutions using multiple Custom agents (for ensemble)
        alt_solutions = []
        for _ in range(2):  # Generate 2 alternative answers for ensemble
            alt_sol = await self.custom(instruction="Solve this problem independently using your own reasoning steps. Be precise.")
            alt_solutions.append(alt_sol)

        # Step 5: Ensemble the main solution and alternatives to select the best one
        final_solution = await self.sc_ensemble(solutions=[reviewed_answer] + alt_solutions)

        return final_solution