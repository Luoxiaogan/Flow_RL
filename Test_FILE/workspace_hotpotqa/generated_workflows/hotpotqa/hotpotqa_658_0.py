# Workflow ID: hotpotqa_658_0
# Benchmark: hotpotqa
# Data Indices: [2805, 2159, 3548, 1645, 995]

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
        It uses sequential reasoning to extract and connect facts, then synthesizes the answer.
        """
        # Step 1: Use FlexibleCustom with sequential reasoning to break down the problem
        reasoning_steps = [
            "identify_key_entities",
            "extract_facts_from_context",
            "find_intermediate_connections",
            "trace_reasoning_path",
            "synthesize_final_answer"
        ]
        multi_hop_solution = await self.flexible_custom(
            custom_instruction="Break down the problem step-by-step and trace logical connections between entities.",
            reasoning_pattern="sequential",
            steps=reasoning_steps
        )

        # Step 2: Use Custom to refine and synthesize the solution from flexible_custom output
        refined_solution = await self.custom(
            instruction="Based on the extracted information, explain the reasoning step-by-step and provide a clear final answer."
        )

        # Step 3: Review the refined solution to validate correctness
        validated_solution = await self.review(pre_solution=refined_solution)

        # Step 4: Ensemble with direct answer generation as a fallback or validation check
        direct_answer = await self.answer_generate()
        solutions = [validated_solution, direct_answer]
        final_answer = await self.sc_ensemble(solutions=solutions)

        return final_answer