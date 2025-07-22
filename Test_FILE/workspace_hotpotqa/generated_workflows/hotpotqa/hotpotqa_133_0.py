# Workflow ID: hotpotqa_133_0
# Benchmark: hotpotqa
# Data Indices: [3031, 1658, 1788, 437, 413]

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
        It uses flexible custom reasoning to break down complex problems step-by-step.
        """
        # Step 1: Use FlexibleCustom with sequential reasoning to extract entities and find connections
        solution = await self.flexible_custom(
            custom_instruction="Break down the problem into key entities and trace logical connections between them.",
            reasoning_pattern="sequential",
            steps=["extract_entities", "find_connections", "trace_reasoning_path", "synthesize_answer"]
        )

        # Step 2: Generate a final answer based on the structured reasoning path
        final_answer = await self.answer_generate()

        # Step 3: Optionally review the generated answer for accuracy
        reviewed_answer = await self.review(pre_solution=final_answer)

        # Step 4: Ensemble with original solution for robustness (if multiple solutions were generated earlier)
        ensemble_solution = await self.sc_ensemble(solutions=[solution, reviewed_answer])

        return ensemble_solution