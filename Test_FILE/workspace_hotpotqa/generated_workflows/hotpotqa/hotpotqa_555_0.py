# Workflow ID: hotpotqa_555_0
# Benchmark: hotpotqa
# Data Indices: [2166, 2817, 2998, 417, 3386]

class Workflow:
    def __init__(
        self,
        config,
        problem
    ) -> None:
        self.problem = problem
        self.config = create(config)
        self.custom = operator.Custom(self.config, self.problem)
        self.sc_ensemble = operator.ScEnsemble(self.config, self.problem)
        self.answer_generate = operator.AnswerGenerate(self.config, self.problem)
        self.review = operator.Review(self.config, self.problem)
        self.flexible_custom = operator.FlexibleCustom(self.config, self.problem)

    async def run_workflow(self):
        """
        This is a workflow graph for multi-hop question answering.
        It uses FlexibleCustom for sequential reasoning to extract and connect facts,
        then Custom to synthesize the answer, and Review to validate the result.
        """
        # Step 1: Use FlexibleCustom with sequential reasoning to break down the problem
        # and trace connections across multiple pieces of information
        reasoning_solution = await self.flexible_custom(
            custom_instruction="Break down the problem step-by-step, identify key entities, and trace logical connections between them.",
            reasoning_pattern="sequential",
            steps=["identify_entities", "find_connections", "trace_reasoning_path", "synthesize_answer"]
        )

        # Step 2: Use Custom to synthesize the final answer based on the structured reasoning
        synthesis_solution = await self.custom(
            instruction="Based on the detailed reasoning above, generate a clear and concise answer that directly addresses the original question."
        )

        # Step 3: Use Review to validate the synthesized solution by checking its internal consistency
        validated_solution = await self.review(
            pre_solution=synthesis_solution
        )

        # Optional: Ensemble with a direct answer from AnswerGenerate for robustness
        direct_answer = await self.answer_generate()
        ensemble_solution = await self.sc_ensemble(solutions=[validated_solution, direct_answer])

        return ensemble_solution