# Workflow ID: hotpotqa_409_0
# Benchmark: hotpotqa
# Data Indices: [875, 1237, 2329, 1224, 3482]

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
        Finally, it reviews the solution for correctness.
        """
        # Step 1: Use FlexibleCustom with sequential reasoning to break down the problem and trace connections
        multi_hop_solution = await self.flexible_custom(
            custom_instruction="Break down the problem into smaller steps, identify key entities, find connections between them, and trace the reasoning path step by step."
        )

        # Step 2: Use Custom to synthesize a coherent answer from the multi-hop solution
        synthesized_answer = await self.custom(
            instruction="Based on the step-by-step reasoning and connections found, generate a clear and concise final answer."
        )

        # Step 3: Review the synthesized answer to improve accuracy
        reviewed_answer = await self.review(pre_solution=synthesized_answer)

        # Step 4: Ensemble with original multi-hop solution to ensure robustness
        ensemble_solution = await self.sc_ensemble(solutions=[multi_hop_solution, reviewed_answer])

        return ensemble_solution