# Workflow ID: hotpotqa_761_0
# Benchmark: hotpotqa
# Data Indices: [1910, 323, 1797, 2243, 2205]

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
        self.sc_ensemble = operator.ScEnsemble(self.config, self.problem)
        self.review = operator.Review(self.config, self.problem)

    async def run_workflow(self):
        """
        This is a workflow graph for multi-hop question answering.
        It uses sequential reasoning to extract and connect facts, then synthesizes the answer.
        Finally, it reviews the solution for correctness.
        """
        # Step 1: Use FlexibleCustom for step-by-step multi-hop reasoning
        multi_hop_solution = await self.flexible_custom(
            custom_instruction="Break down the problem into smaller steps and explain the reasoning behind each step."
        )

        # Step 2: Use Custom to synthesize the final answer from the multi-hop reasoning
        synthesized_answer = await self.custom(
            instruction="Based on the reasoning above, generate a concise and accurate answer to the question."
        )

        # Step 3: Review the synthesized answer for accuracy and clarity
        reviewed_answer = await self.review(pre_solution=synthesized_answer)

        # Step 4: Ensemble with original multi-hop solution to improve robustness
        solutions = [multi_hop_solution, reviewed_answer]
        final_answer = await self.sc_ensemble(solutions=solutions)

        return final_answer