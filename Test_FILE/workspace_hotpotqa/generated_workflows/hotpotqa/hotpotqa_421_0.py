# Workflow ID: hotpotqa_421_0
# Benchmark: hotpotqa
# Data Indices: [1778, 1874, 1948, 3791]

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
        Uses flexible custom reasoning to break down the problem step-by-step.
        """
        # Step 1: Use FlexibleCustom with sequential reasoning to extract entities and trace connections
        solution = await self.flexible_custom(
            custom_instruction="Break down the problem into steps: identify key entities, find logical connections between them, and synthesize the final answer.",
            reasoning_pattern="sequential",
            steps=["extract_entities", "find_connections", "synthesize_answer"]
        )

        # Step 2: Optionally refine the solution using Review if needed
        refined_solution = await self.review(pre_solution=solution)

        # Step 3: Generate final answer directly (as fallback or confirmation)
        final_answer = await self.answer_generate()

        # Step 4: Ensemble multiple solutions for robustness (if we have more than one)
        solutions = [refined_solution, final_answer]
        ensembled_solution = await self.sc_ensemble(solutions=solutions)

        return ensembled_solution