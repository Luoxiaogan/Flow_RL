# Workflow ID: hotpotqa_296_0
# Benchmark: hotpotqa
# Data Indices: [406, 955, 1828, 655, 2911]

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
        It uses sequential reasoning to extract and connect facts, then synthesizes the answer.
        """
        # Step 1: Use FlexibleCustom with sequential reasoning to break down the problem
        # and trace connections between pieces of information in the context
        multi_hop_reasoning = await self.flexible_custom(
            custom_instruction="Break down the problem step by step and trace logical connections between facts.",
            reasoning_pattern="sequential",
            steps=["identify_key_entities", "find_intermediate_connections", "trace_reasoning_path", "synthesize_answer"]
        )

        # Step 2: Use Custom to synthesize a coherent answer based on the structured reasoning
        synthesized_answer = await self.custom(instruction="Based on the multi-hop reasoning, generate a clear and concise answer with justification.")

        # Step 3: Review the synthesized answer to ensure correctness and completeness
        final_answer = await self.review(pre_solution=synthesized_answer)

        # Optional: Ensemble with a second independent solution for robustness
        # Generate an alternative path using a different instruction to avoid bias
        alternate_solution = await self.custom(instruction="Solve this problem by identifying key facts first, then connecting them logically step-by-step.")
        
        # Ensembling both solutions improves accuracy
        ensemble_result = await self.sc_ensemble(solutions=[final_answer, alternate_solution])

        return ensemble_result