# Workflow ID: hotpotqa_379_0
# Benchmark: hotpotqa
# Data Indices: [365, 1643, 3047, 3985, 2940]

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
        """
        # Step 1: Use FlexibleCustom with sequential reasoning to trace connections step-by-step
        solution = await self.flexible_custom(
            custom_instruction="Break down the problem into smaller steps and explain the reasoning behind each step.",
            reasoning_pattern="sequential",
            steps=["identify_key_entities", "find_intermediate_connections", "trace_reasoning_path", "synthesize_answer"]
        )

        # Step 2: Generate an answer directly as a baseline
        baseline_answer = await self.answer_generate()

        # Step 3: Review the initial solution to refine it
        refined_solution = await self.review(pre_solution=solution)

        # Step 4: Ensemble the baseline and refined solutions for improved accuracy
        ensemble_solution = await self.sc_ensemble(solutions=[baseline_answer, refined_solution])

        return ensemble_solution