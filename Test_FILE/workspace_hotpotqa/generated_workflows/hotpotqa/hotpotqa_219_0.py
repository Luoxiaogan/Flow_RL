# Workflow ID: hotpotqa_219_0
# Benchmark: hotpotqa
# Data Indices: [119, 757, 3949, 2421, 3954]

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
        Uses FlexibleCustom with structured reasoning steps to solve complex questions.
        """
        # Step 1: Use FlexibleCustom for structured multi-hop reasoning
        solution = await self.flexible_custom(
            custom_instruction="Break down the problem into key entities and connections between them.",
            reasoning_pattern="sequential",
            steps=["extract_entities", "find_connections", "trace_reasoning_path", "synthesize_answer"]
        )

        # Step 2: Optionally review the generated solution for refinement
        reviewed_solution = await self.review(pre_solution=solution)

        # Step 3: Generate final answer using direct generation (as fallback or confirmation)
        final_answer = await self.answer_generate()

        # Step 4: Ensemble the flexible custom result and direct answer for robustness
        ensemble_result = await self.sc_ensemble(solutions=[reviewed_solution, final_answer])

        return ensemble_result