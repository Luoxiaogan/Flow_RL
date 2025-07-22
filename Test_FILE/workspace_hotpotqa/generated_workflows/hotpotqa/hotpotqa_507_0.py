# Workflow ID: hotpotqa_507_0
# Benchmark: hotpotqa
# Data Indices: [647, 105, 2846, 2359]

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
        It uses FlexibleCustom (sequential reasoning) to extract and connect facts,
        then Custom to synthesize the answer, and Review to validate it.
        """
        # Step 1: Use FlexibleCustom with sequential reasoning to break down the problem
        # and trace connections between pieces of information.
        fact_extraction = await self.flexible_custom(
            custom_instruction="Break down the problem into smaller steps and trace how each piece of information connects to the next.",
            reasoning_pattern="sequential",
            steps=["identify_key_entities", "find_intermediate_connections", "trace_reasoning_path", "synthesize_answer"]
        )

        # Step 2: Use Custom to generate a synthesized answer based on extracted facts.
        synthesis = await self.custom(
            instruction="Based on the reasoning path above, explain how each step leads to the final answer. Be detailed and logical."
        )

        # Step 3: Use Review to check the validity and coherence of the synthesized answer.
        validated_answer = await self.review(pre_solution=synthesis)

        # Step 4: Ensemble multiple solutions if needed — here we simulate a simple ensemble
        # by generating one more solution via direct AnswerGenerate and ensembling.
        direct_answer = await self.answer_generate()
        solution_list = [validated_answer, direct_answer]
        final_answer = await self.sc_ensemble(solutions=solution_list)

        return final_answer