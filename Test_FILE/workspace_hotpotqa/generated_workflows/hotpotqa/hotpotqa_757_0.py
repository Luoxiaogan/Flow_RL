# Workflow ID: hotpotqa_757_0
# Benchmark: hotpotqa
# Data Indices: [3108, 2151, 825, 2218]

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
        This is a workflow graph for multi-hop question answering using sequential reasoning.
        It traces connections step-by-step through the context to solve complex questions.
        """
        # Step 1: Use FlexibleCustom with sequential multi-hop pattern to break down and trace reasoning
        solution = await self.flexible_custom(
            custom_instruction="Break down the problem into smaller steps and trace connections between pieces of information sequentially.",
            reasoning_pattern="sequential",
            steps=["identify_key_entities", "find_intermediate_connections", "trace_reasoning_path", "synthesize_final_answer"]
        )

        # Step 2: Review the generated solution for clarity and correctness
        reviewed_solution = await self.review(pre_solution=solution)

        # Step 3: Generate final answer based on the reviewed solution
        final_answer = await self.answer_generate()

        # Optional: Ensemble with original solution if needed (for robustness)
        ensemble_result = await self.sc_ensemble(solutions=[solution, reviewed_solution, final_answer])

        return ensemble_result