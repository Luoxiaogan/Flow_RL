# Workflow ID: hotpotqa_286_0
# Benchmark: hotpotqa
# Data Indices: [3118, 2939, 3793, 3891, 1996]

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
        It breaks down the problem into steps, traces connections across context, and refines the answer.
        """
        # Step 1: Use FlexibleCustom with sequential reasoning to trace multi-hop connections
        solution = await self.flexible_custom(
            custom_instruction="Break down the problem step-by-step, identifying key entities and their relationships across the context.",
            reasoning_pattern="sequential",
            steps=["identify_entities", "find_connections", "trace_reasoning_path", "synthesize_answer"]
        )

        # Step 2: Review the generated solution to refine it
        reviewed_solution = await self.review(pre_solution=solution)

        # Step 3: Generate final answer based on the refined solution
        final_answer = await self.answer_generate()

        # Optional: Ensemble multiple solutions if needed (e.g., from different reasoning paths)
        # Here we use a simple list of two solutions: original and reviewed
        ensemble_input = [solution, reviewed_solution]
        ensembled_answer = await self.sc_ensemble(solutions=ensemble_input)

        return ensembled_answer