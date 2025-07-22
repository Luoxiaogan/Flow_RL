# Workflow ID: hotpotqa_7_0
# Benchmark: hotpotqa
# Data Indices: [1990, 3699, 640, 196, 3543]

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
        # and extract key facts from the context step by step
        fact_extraction = await self.flexible_custom(
            custom_instruction="Break down the problem into smaller steps and extract relevant facts sequentially.",
            reasoning_pattern="sequential",
            steps=["identify_key_entities", "extract_facts", "connect_information", "synthesize_answer"]
        )

        # Step 2: Use Custom to synthesize the extracted facts into a coherent answer
        synthesis = await self.custom(
            instruction="Based on the facts you've extracted, explain how they lead to the final answer. Think step-by-step."
        )

        # Step 3: Use Review to validate the synthesized solution
        validated_solution = await self.review(pre_solution=synthesis)

        # Step 4: Ensemble multiple solutions (generate two different answers via Custom)
        answer1 = await self.answer_generate()
        answer2 = await self.custom(instruction="Solve this problem using detailed reasoning and clear steps.")
        ensemble = await self.sc_ensemble(solutions=[answer1, answer2, validated_solution])

        return ensemble