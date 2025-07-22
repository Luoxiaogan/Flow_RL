# Workflow ID: hotpotqa_72_0
# Benchmark: hotpotqa
# Data Indices: [1132, 1934, 618, 2479]

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
        and refines the solution through review and ensemble techniques.
        """
        # Step 1: Use flexible custom to trace multi-hop reasoning sequentially
        multi_hop_solution = await self.flexible_custom(
            custom_instruction="Break down the problem step-by-step, identifying key entities and connecting them logically.",
            reasoning_pattern="sequential",
            steps=["identify_question_components", "extract_relevant_context", "trace_information_paths", "synthesize_final_answer"]
        )

        # Step 2: Generate an initial answer directly (for comparison/ensemble)
        direct_answer = await self.answer_generate()

        # Step 3: Ensemble the two solutions to improve accuracy
        final_solution = await self.sc_ensemble(solutions=[multi_hop_solution, direct_answer])

        # Step 4: Review the ensembled solution for refinement
        refined_solution = await self.review(pre_solution=final_solution)

        return refined_solution