# Workflow ID: hotpotqa_446_0
# Benchmark: hotpotqa
# Data Indices: [965, 2984, 2517, 910]

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
        # Step 1: Use flexible custom to trace multi-hop connections sequentially
        solution = await self.flexible_custom(
            custom_instruction="Break down the problem step-by-step, identifying key entities and connecting them through logical reasoning paths.",
            reasoning_pattern="sequential",
            steps=["identify_entities", "find_connections", "trace_reasoning_path", "synthesize_answer"]
        )

        # Step 2: Generate an answer directly as a baseline
        baseline_answer = await self.answer_generate()

        # Step 3: Review the flexible custom solution to refine it
        refined_solution = await self.review(pre_solution=solution)

        # Step 4: Ensemble the flexible custom result and the baseline answer
        final_answer = await self.sc_ensemble(solutions=[refined_solution, baseline_answer])

        return final_answer