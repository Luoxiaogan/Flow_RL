# Workflow ID: hotpotqa_602_0
# Benchmark: hotpotqa
# Data Indices: [2732, 2389, 1111, 2201, 1936]

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
        It first generates an initial answer, then uses flexible custom to trace multi-hop connections step-by-step,
        and finally ensembles the results to improve accuracy.
        """
        # Step 1: Generate an initial answer as baseline
        initial_answer = await self.answer_generate()

        # Step 2: Use FlexibleCustom with sequential reasoning to trace multi-hop connections
        # This operator breaks down the problem into steps and builds a reasoned path
        multi_hop_solution = await self.flexible_custom(
            custom_instruction="Break down the problem into smaller steps and trace connections between facts logically.",
            reasoning_pattern="sequential",
            steps=["identify_key_entities", "find_intermediate_connections", "trace_reasoning_path", "synthesize_final_answer"]
        )

        # Step 3: Review the initial answer using the multi-hop solution as context
        refined_answer = await self.review(pre_solution=initial_answer)

        # Step 4: Ensemble the initial and refined answers to select the best solution
        ensemble_solution = await self.sc_ensemble(solutions=[initial_answer, multi_hop_solution, refined_answer])

        return ensemble_solution