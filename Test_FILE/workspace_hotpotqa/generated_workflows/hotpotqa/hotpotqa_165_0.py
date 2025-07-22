# Workflow ID: hotpotqa_165_0
# Benchmark: hotpotqa
# Data Indices: [1071, 399, 2491, 1635]

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
        It uses sequential reasoning to extract and connect facts, then synthesizes the answer with review for validation.
        """
        # Step 1: Use FlexibleCustom with sequential reasoning to break down the problem into steps
        sequential_reasoning = await self.flexible_custom(
            custom_instruction="Break down the problem step by step, identifying key entities and relationships across multiple pieces of information.",
            reasoning_pattern="sequential",
            steps=["identify_entities", "find_connections", "trace_reasoning_path", "synthesize_answer"]
        )

        # Step 2: Use Custom to synthesize a detailed answer based on the structured reasoning
        synthesis = await self.custom(
            instruction="Based on the structured reasoning above, explain how each piece of information connects to form a complete answer. Be clear and logical in your explanation."
        )

        # Step 3: Generate an initial answer using AnswerGenerate for baseline
        initial_answer = await self.answer_generate()

        # Step 4: Ensemble the synthesis and initial answer to improve robustness
        solutions = [synthesis, initial_answer]
        ensembled_solution = await self.sc_ensemble(solutions=solutions)

        # Step 5: Review the ensembled solution to validate and refine
        final_answer = await self.review(pre_solution=ensembled_solution)

        return final_answer