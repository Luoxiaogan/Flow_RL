# Workflow ID: hotpotqa_279_0
# Benchmark: hotpotqa
# Data Indices: [3757, 2910, 1346, 3296, 938]

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
        It breaks down the problem into steps, traces connections across sources, and refines the solution.
        """
        # Step 1: Use FlexibleCustom with Sequential Multi-Hop to trace connections step-by-step
        solution_1 = await self.flexible_custom(
            custom_instruction="Break down the problem into smaller steps and explain the reasoning behind each step.",
            reasoning_pattern="sequential",
            steps=["identify_key_entities", "find_intermediate_connections", "trace_reasoning_path", "synthesize_answer"]
        )

        # Step 2: Generate an answer directly (baseline)
        solution_2 = await self.answer_generate()

        # Step 3: Review the first solution to refine it
        refined_solution = await self.review(pre_solution=solution_1)

        # Step 4: Ensemble the two solutions (original + refined) to improve accuracy
        ensemble_solution = await self.sc_ensemble(solutions=[solution_2, refined_solution])

        return ensemble_solution