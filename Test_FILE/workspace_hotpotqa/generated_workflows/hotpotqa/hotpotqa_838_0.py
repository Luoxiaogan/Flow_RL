# Workflow ID: hotpotqa_838_0
# Benchmark: hotpotqa
# Data Indices: [3702, 3774, 1478, 1272, 3099]

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
        It breaks down the problem into steps, traces connections across context, and refines the solution.
        """
        # Step 1: Use FlexibleCustom for sequential multi-hop reasoning to trace connections step-by-step
        solution = await self.flexible_custom(
            custom_instruction="Break down the problem into smaller steps and explain the reasoning behind each step to connect information across different parts of the context.",
            reasoning_pattern="sequential",
            steps=["identify_key_entities", "find_intermediate_connections", "trace_reasoning_path", "synthesize_final_answer"]
        )

        # Step 2: Generate a direct answer as a baseline for ensemble
        direct_answer = await self.answer_generate()

        # Step 3: Review the flexible custom solution to refine it
        refined_solution = await self.review(pre_solution=solution)

        # Step 4: Ensemble the direct answer and the refined solution to improve accuracy
        final_solution = await self.sc_ensemble(solutions=[direct_answer, refined_solution])

        return final_solution