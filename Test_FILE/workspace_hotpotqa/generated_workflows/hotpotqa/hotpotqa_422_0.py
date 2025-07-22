# Workflow ID: hotpotqa_422_0
# Benchmark: hotpotqa
# Data Indices: [2134, 2453, 552, 921]

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
        # and trace connections between pieces of information
        reasoning_solution = await self.flexible_custom(
            custom_instruction="Break down the problem step by step and trace how each piece of evidence connects to the final answer.",
            reasoning_pattern="sequential",
            steps=["identify_key_entities", "extract_relevant_facts", "connect_information_paths", "synthesize_answer"]
        )

        # Step 2: Use Custom to refine and synthesize the solution from the flexible custom output
        synthesized_solution = await self.custom(
            instruction="Based on the reasoning above, clearly state the final answer with concise justification."
        )

        # Step 3: Review the synthesized solution to improve clarity and correctness
        reviewed_solution = await self.review(pre_solution=synthesized_solution)

        # Step 4: Generate a direct answer as a baseline for ensemble (optional but useful)
        direct_answer = await self.answer_generate()

        # Step 5: Ensemble the reviewed solution and the direct answer to select the best one
        final_answer = await self.sc_ensemble(solutions=[reviewed_solution, direct_answer])

        return final_answer