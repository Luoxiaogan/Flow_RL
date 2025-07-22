# Workflow ID: hotpotqa_104_0
# Benchmark: hotpotqa
# Data Indices: [2882, 787, 295, 710, 764]

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
        It breaks down the problem into steps, traces connections between pieces of information,
        and refines the answer through review and ensemble techniques.
        """
        # Step 1: Use flexible custom to trace multi-hop connections sequentially
        solution = await self.flexible_custom(
            custom_instruction="Break down the problem step-by-step, identifying key entities and connecting them logically across different parts of the context.",
            reasoning_pattern="sequential",
            steps=["identify_entities", "find_connections", "trace_reasoning_path", "synthesize_answer"]
        )

        # Step 2: Generate a direct answer as a baseline
        baseline_answer = await self.answer_generate()

        # Step 3: Review the initial solution to improve clarity and correctness
        refined_solution = await self.review(pre_solution=solution)

        # Step 4: Ensemble the baseline and refined solutions for robustness
        final_solution = await self.sc_ensemble(solutions=[baseline_answer, refined_solution])

        return final_solution