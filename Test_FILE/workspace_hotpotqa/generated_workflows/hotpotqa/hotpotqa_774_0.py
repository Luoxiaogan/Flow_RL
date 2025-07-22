# Workflow ID: hotpotqa_774_0
# Benchmark: hotpotqa
# Data Indices: [1912, 3694, 3173, 3976]

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
        It traces connections step-by-step through the context to solve complex problems.
        """
        # Step 1: Use FlexibleCustom with sequential pattern to break down the problem into logical steps
        solution = await self.flexible_custom(
            custom_instruction="Break down the problem into smaller steps and trace connections between them logically.",
            reasoning_pattern="sequential",
            steps=["identify_key_entities", "find_intermediate_connections", "trace_reasoning_path", "synthesize_final_answer"]
        )

        # Step 2: Generate an answer based on the structured reasoning path
        final_answer = await self.answer_generate()

        # Step 3: Review the generated answer to ensure clarity and correctness
        reviewed_answer = await self.review(pre_solution=final_answer)

        # Step 4: Ensemble with original solution to improve robustness (optional but effective for multi-hop)
        ensemble_solution = await self.sc_ensemble(solutions=[solution, reviewed_answer])

        return ensemble_solution