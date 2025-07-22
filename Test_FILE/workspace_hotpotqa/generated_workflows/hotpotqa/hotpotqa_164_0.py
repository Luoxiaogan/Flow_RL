# Workflow ID: hotpotqa_164_0
# Benchmark: hotpotqa
# Data Indices: [650, 3396, 774, 1426]

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
        It uses FlexibleCustom for structured multi-hop reasoning, 
        Custom for synthesis, and Review for validation.
        """
        # Step 1: Use FlexibleCustom with sequential reasoning to extract and connect facts
        solution_step1 = await self.flexible_custom(
            custom_instruction="Break down the problem into smaller steps and trace connections between pieces of information.",
            reasoning_pattern="sequential",
            steps=["identify_key_entities", "extract_relevant_facts", "connect_information_paths", "synthesize_intermediate_answer"]
        )

        # Step 2: Use Custom to synthesize a clear, step-by-step explanation based on the intermediate solution
        solution_step2 = await self.custom(
            instruction="Based on the intermediate solution, explain how each piece of evidence leads to the final answer. Be thorough and logical."
        )

        # Step 3: Use Review to validate and refine the synthesized solution
        refined_solution = await self.review(pre_solution=solution_step2)

        # Step 4: Generate final answer using AnswerGenerate (optional, but ensures robustness)
        final_answer = await self.answer_generate()

        # Ensemble the refined solution and final answer for best output
        ensemble_output = await self.sc_ensemble(solutions=[refined_solution, final_answer])

        return ensemble_output