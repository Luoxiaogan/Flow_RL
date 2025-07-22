# Workflow ID: hotpotqa_753_0
# Benchmark: hotpotqa
# Data Indices: [1414, 3025, 2719, 2274, 289]

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
        It uses sequential reasoning to extract and connect facts, then synthesizes the answer.
        """
        # Step 1: Use FlexibleCustom with sequential reasoning to break down the problem into steps
        reasoning_steps = ["identify_key_entities", "find_intermediate_connections", "trace_reasoning_path", "synthesize_answer"]
        solution = await self.flexible_custom(
            custom_instruction="Break down the problem step-by-step and trace how each piece of information connects to the final answer.",
            reasoning_pattern="sequential",
            steps=reasoning_steps
        )

        # Step 2: Generate a synthesis using Custom to explain the reasoning in detail
        detailed_solution = await self.custom(
            instruction="Explain how to solve this problem by breaking it down into detailed steps and explaining the reasoning behind each step."
        )

        # Step 3: Ensemble multiple solutions (if needed) — here we use both outputs
        solutions = [solution, detailed_solution]
        ensembled_solution = await self.sc_ensemble(solutions=solutions)

        # Step 4: Review the ensembled solution to refine and validate
        final_solution = await self.review(pre_solution=ensembled_solution)

        return final_solution