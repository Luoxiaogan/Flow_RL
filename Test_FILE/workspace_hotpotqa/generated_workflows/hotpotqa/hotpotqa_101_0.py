# Workflow ID: hotpotqa_101_0
# Benchmark: hotpotqa
# Data Indices: [772, 2455, 1850, 2312, 1405]

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
        It breaks down the problem into smaller steps and traces connections across context.
        """
        # Step 1: Use FlexibleCustom with sequential reasoning to trace multi-hop connections
        solution = await self.flexible_custom(
            custom_instruction="Break down the problem step by step and trace how information connects across different parts of the context.",
            reasoning_pattern="sequential",
            steps=["identify_key_entities", "find_intermediate_connections", "trace_reasoning_path", "synthesize_final_answer"]
        )

        # Step 2: Review the generated solution to refine it
        reviewed_solution = await self.review(pre_solution=solution)

        # Step 3: Generate a final answer based on the refined solution
        final_answer = await self.answer_generate()

        # Step 4: Ensemble multiple solutions (including original and reviewed) for robustness
        ensemble_solutions = [solution, reviewed_solution, final_answer]
        ensembled_answer = await self.sc_ensemble(solutions=ensemble_solutions)

        return ensembled_answer