# Workflow ID: hotpotqa_819_0
# Benchmark: hotpotqa
# Data Indices: [1636, 3326, 2091, 2406]

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
                                                      steps=["extract_facts", "identify_connections", "trace_reasoning_path", "synthesize_answer"])
        self.custom = operator.Custom(self.config, self.problem)
        self.review = operator.Review(self.config, self.problem)
        self.sc_ensemble = operator.ScEnsemble(self.config, self.problem)

    async def run_workflow(self):
        """
        This is a workflow graph for multi-hop question answering.
        It uses sequential reasoning to extract and connect facts, then synthesizes an answer,
        followed by review for validation, and finally ensembles multiple solutions for robustness.
        """
        # Step 1: Use FlexibleCustom with sequential reasoning to trace multi-hop connections
        multi_hop_solution = await self.flexible_custom(
            custom_instruction="Break down the problem into smaller steps and explain the reasoning behind each step to identify key facts and their connections."
        )

        # Step 2: Generate an initial answer using Custom (for synthesis based on extracted facts)
        synthesized_answer = await self.custom(
            instruction="Based on the reasoning steps above, synthesize a clear and concise answer to the original question."
        )

        # Step 3: Review the synthesized answer for accuracy and completeness
        reviewed_answer = await self.review(
            pre_solution=synthesized_answer
        )

        # Step 4: Ensemble with a few alternative solutions to improve robustness
        solution_list = [
            multi_hop_solution,
            synthesized_answer,
            reviewed_answer
        ]
        final_answer = await self.sc_ensemble(solutions=solution_list)

        return final_answer