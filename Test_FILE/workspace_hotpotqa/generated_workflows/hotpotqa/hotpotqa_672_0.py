# Workflow ID: hotpotqa_672_0
# Benchmark: hotpotqa
# Data Indices: [1361, 299, 2726, 3651]

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
        It breaks down the problem into smaller steps and connects information across different sources.
        """
        # Step 1: Use FlexibleCustom with sequential reasoning to trace multi-hop connections
        solution = await self.flexible_custom(
            custom_instruction="Break down the problem step-by-step and connect relevant information from different parts of the context.",
            reasoning_pattern="sequential",
            steps=["identify_key_entities", "find_intermediate_connections", "trace_reasoning_path", "synthesize_final_answer"]
        )

        # Step 2: Generate an answer based on the structured reasoning path
        final_answer = await self.answer_generate()

        # Step 3: Review the generated answer for accuracy and completeness
        reviewed_answer = await self.review(pre_solution=final_answer)

        # Step 4: Ensemble with initial solution (from flexible_custom) to improve robustness
        solutions = [solution, reviewed_answer]
        ensembled_answer = await self.sc_ensemble(solutions=solutions)

        return ensembled_answer