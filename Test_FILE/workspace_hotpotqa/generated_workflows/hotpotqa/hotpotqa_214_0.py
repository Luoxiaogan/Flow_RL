# Workflow ID: hotpotqa_214_0
# Benchmark: hotpotqa
# Data Indices: [3773, 3932, 2066, 2920]

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
        This is a workflow graph for multi-hop question answering using sequential reasoning.
        """
        # Step 1: Use FlexibleCustom to perform step-by-step multi-hop reasoning
        multi_hop_solution = await self.flexible_custom(
            custom_instruction="Break down the problem into smaller steps and trace connections between pieces of information.",
            reasoning_pattern="sequential",
            steps=["identify_key_entities", "find_intermediate_connections", "trace_reasoning_path", "synthesize_final_answer"]
        )

        # Step 2: Generate an answer based on the multi-hop solution
        final_answer = await self.answer_generate()

        # Step 3: Review the generated answer to improve accuracy
        refined_answer = await self.review(pre_solution=final_answer)

        # Step 4: Ensemble with original multi-hop solution for robustness
        ensemble_solution = await self.sc_ensemble(solutions=[refined_answer, multi_hop_solution])

        return ensemble_solution