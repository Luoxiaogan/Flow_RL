# Workflow ID: hotpotqa_234_0
# Benchmark: hotpotqa
# Data Indices: [3344, 2614, 2296, 617, 2465]

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
                                                      steps=["identify_key_facts", "extract_entities", "find_connections", "synthesize_reasoning"])
        self.custom = operator.Custom(self.config, self.problem)
        self.sc_ensemble = operator.ScEnsemble(self.config, self.problem)
        self.review = operator.Review(self.config, self.problem)
        self.answer_generate = operator.AnswerGenerate(self.config, self.problem)

    async def run_workflow(self):
        """
        This is a workflow graph for multi-hop question answering.
        It uses sequential reasoning to extract and connect facts, then synthesizes the answer.
        """
        # Step 1: Use FlexibleCustom with sequential reasoning to break down the problem
        multi_hop_analysis = await self.flexible_custom(
            custom_instruction="Break down the problem into smaller steps and explain the reasoning behind each step."
        )

        # Step 2: Use Custom to synthesize the answer from the structured analysis
        synthesized_answer = await self.custom(
            instruction="Based on the multi-hop reasoning above, generate a clear and concise answer to the question."
        )

        # Step 3: Review the synthesized answer for accuracy and clarity
        reviewed_answer = await self.review(pre_solution=synthesized_answer)

        # Step 4: Generate final answer using AnswerGenerate for consistency
        final_answer = await self.answer_generate()

        # Step 5: Ensemble multiple solutions (synthesized + reviewed + generated) for robustness
        ensemble_solution = await self.sc_ensemble(solutions=[synthesized_answer, reviewed_answer, final_answer])

        return ensemble_solution