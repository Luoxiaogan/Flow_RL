# Workflow ID: hotpotqa_788_0
# Benchmark: hotpotqa
# Data Indices: [2764, 391, 1701, 2046, 991]

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
        # Step 1: Use FlexibleCustom with sequential reasoning to break down the problem into steps
        sequential_reasoning = await self.flexible_custom(
            custom_instruction="Break down the problem into smaller, logical steps for multi-hop reasoning.",
            reasoning_pattern="sequential",
            steps=["identify_question_components", "extract_relevant_facts", "connect_information", "synthesize_answer"]
        )

        # Step 2: Use Custom to synthesize an answer based on the structured reasoning path
        synthesis = await self.custom(
            instruction="Based on the structured reasoning steps, synthesize a clear and accurate answer."
        )

        # Step 3: Review the synthesized answer to validate logic and correctness
        reviewed_answer = await self.review(pre_solution=synthesis)

        # Step 4: Generate final answer using AnswerGenerate as a fallback or supplementary step
        final_answer = await self.answer_generate()

        # Step 5: Ensemble multiple solutions (synthesis + reviewed + generated) to improve robustness
        ensemble_solution = await self.sc_ensemble(solutions=[synthesis, reviewed_answer, final_answer])

        return ensemble_solution