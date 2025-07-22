# Workflow ID: hotpotqa_700_0
# Benchmark: hotpotqa
# Data Indices: [671, 3293, 49, 2086, 657]

class Workflow:
    def __init__(
        self,
        config,
        problem
    ) -> None:
        self.problem = problem
        self.config = create(config)
        self.flexible_custom = operator.FlexibleCustom(self.config, self.problem,
                                                       reasoning_pattern="sequential",
                                                       steps=["identify_entities", "find_connections", "trace_reasoning_path", "synthesize_answer"])
        self.custom = operator.Custom(self.config, self.problem)
        self.sc_ensemble = operator.ScEnsemble(self.config, self.problem)
        self.review = operator.Review(self.config, self.problem)

    async def run_workflow(self):
        """
        This is a workflow graph for multi-hop question answering.
        It uses sequential reasoning to extract and connect facts, then synthesizes the answer.
        """
        # Step 1: Use FlexibleCustom with sequential reasoning to break down and trace the multi-hop logic
        initial_solution = await self.flexible_custom(
            custom_instruction="Break down the problem into smaller steps, identify key entities, and trace logical connections between them."
        )

        # Step 2: Use Custom to synthesize a clear, structured answer based on the traced path
        synthesized_answer = await self.custom(
            instruction="Based on the reasoning path identified above, generate a clear and concise final answer. Ensure all intermediate steps are logically connected."
        )

        # Step 3: Ensemble multiple solutions (simulate with one additional step for robustness)
        solution_list = [initial_solution, synthesized_answer]
        ensembled_solution = await self.sc_ensemble(solutions=solution_list)

        # Step 4: Review the ensembled solution to catch errors or inconsistencies
        final_answer = await self.review(pre_solution=ensembled_solution)

        return final_answer