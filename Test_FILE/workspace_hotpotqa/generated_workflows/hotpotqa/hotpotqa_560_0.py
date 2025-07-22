# Workflow ID: hotpotqa_560_0
# Benchmark: hotpotqa
# Data Indices: [294, 141, 1883, 900, 338]

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
        self.answer_generate = operator.AnswerGenerate(self.config, self.problem)

    async def run_workflow(self):
        """
        This is a workflow graph for multi-hop question answering.
        It uses FlexibleCustom for structured multi-hop reasoning, followed by Custom for synthesis,
        and Review for validation. Ensemble is used to consolidate solutions from multiple paths.
        """
        # Step 1: Use FlexibleCustom with sequential reasoning to break down the problem into smaller steps
        multi_hop_solution = await self.flexible_custom(
            custom_instruction="Break down the problem step-by-step, identifying key facts and connections between them.",
            reasoning_pattern="sequential",
            steps=["identify_key_entities", "extract_relations", "trace_reasoning_path", "synthesize_answer"]
        )

        # Step 2: Use Custom to synthesize a coherent answer based on the multi-hop solution
        synthesized_answer = await self.custom(instruction="Based on the multi-hop reasoning, write a clear and concise answer with logical justification.")

        # Step 3: Generate alternative solutions using AnswerGenerate for ensemble diversity
        direct_answer = await self.answer_generate()

        # Step 4: Ensemble the solutions to select the best one
        solutions = [multi_hop_solution, synthesized_answer, direct_answer]
        ensembled_solution = await self.sc_ensemble(solutions=solutions)

        # Step 5: Review the final ensembled solution to refine it further
        final_answer = await self.review(pre_solution=ensembled_solution)

        return final_answer