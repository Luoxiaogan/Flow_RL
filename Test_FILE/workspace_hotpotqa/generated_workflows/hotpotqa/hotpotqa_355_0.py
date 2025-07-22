# Workflow ID: hotpotqa_355_0
# Benchmark: hotpotqa
# Data Indices: [3467, 1164, 189, 3857, 2872]

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
        It uses flexible custom for step-by-step reasoning, then synthesizes with custom, and validates with review.
        """
        # Step 1: Use FlexibleCustom with sequential reasoning to extract and connect facts
        solution_1 = await self.flexible_custom(
            custom_instruction="Break down the problem into smaller steps and explain the reasoning behind each step.",
            reasoning_pattern="sequential",
            steps=["identify_key_entities", "find_intermediate_connections", "trace_reasoning_path", "synthesize_answer"]
        )

        # Step 2: Generate an initial answer using AnswerGenerate for baseline
        solution_2 = await self.answer_generate()

        # Step 3: Synthesize the extracted information from FlexibleCustom with a custom instruction
        solution_3 = await self.custom(instruction="Based on the previous reasoning, synthesize a clear and accurate final answer.")

        # Step 4: Review the synthesized answer to refine it
        final_solution = await self.review(pre_solution=solution_3)

        # Optional: Ensemble multiple solutions for robustness (if needed)
        ensemble_input = [solution_1, solution_2, solution_3]
        if len(ensemble_input) > 1:
            final_solution = await self.sc_ensemble(solutions=ensemble_input)

        return final_solution