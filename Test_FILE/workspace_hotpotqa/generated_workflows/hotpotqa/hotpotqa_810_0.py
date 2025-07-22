# Workflow ID: hotpotqa_810_0
# Benchmark: hotpotqa
# Data Indices: [3364, 3805, 1323, 3936]

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
                                                      steps=["identify_key_entities", "extract_facts", "connect_information", "synthesize_answer"])
        self.custom = operator.Custom(self.config, self.problem)
        self.sc_ensemble = operator.ScEnsemble(self.config, self.problem)
        self.review = operator.Review(self.config, self.problem)

    async def run_workflow(self):
        """
        This is a workflow graph for multi-hop question answering.
        It uses sequential reasoning to extract and connect facts, then synthesizes the answer.
        A review step ensures correctness before final output.
        """
        # Step 1: Use FlexibleCustom for structured multi-hop reasoning
        multi_hop_solution = await self.flexible_custom(
            custom_instruction="Break down the problem into smaller steps, extract relevant facts, and trace connections between them."
        )

        # Step 2: Generate an initial synthesis using Custom
        synthesized_solution = await self.custom(
            instruction="Based on the extracted information, synthesize a clear and concise answer with reasoning steps."
        )

        # Step 3: Ensemble multiple solutions (simulate by generating two variations)
        solution_list = [
            multi_hop_solution,
            synthesized_solution
        ]
        ensembled_solution = await self.sc_ensemble(solutions=solution_list)

        # Step 4: Review the final solution for accuracy and clarity
        final_answer = await self.review(pre_solution=ensembled_solution)

        return final_answer