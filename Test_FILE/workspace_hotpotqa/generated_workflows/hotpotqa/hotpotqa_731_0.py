# Workflow ID: hotpotqa_731_0
# Benchmark: hotpotqa
# Data Indices: [198, 1490, 998, 1438, 2381]

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
        This is a workflow graph for multi-hop question answering.
        It uses multiple reasoning paths and ensembles the best solution.
        """
        # Step 1: Generate an initial answer using direct reasoning
        direct_answer = await self.answer_generate()

        # Step 2: Use flexible custom with sequential reasoning to trace multi-hop logic
        seq_reasoning = await self.flexible_custom(
            custom_instruction="Break down the problem into logical steps and reason through each step carefully.",
            reasoning_pattern="sequential",
            steps=["identify_key_entities", "find_intermediate_connections", "trace_logical_path", "synthesize_final_answer"]
        )

        # Step 3: Use flexible custom with iterative refinement for accuracy
        iter_refinement = await self.flexible_custom(
            custom_instruction="Start with an initial hypothesis, then verify facts and refine your answer progressively.",
            reasoning_pattern="iterative",
            steps=["initial_hypothesis", "verify_facts", "refine_answer"],
            max_iterations=3
        )

        # Step 4: Ensemble the three solutions to select the best one
        solutions = [direct_answer, seq_reasoning, iter_refinement]
        final_answer = await self.sc_ensemble(solutions=solutions)

        # Step 5: Final review to ensure coherence and correctness
        final_solution = await self.review(pre_solution=final_answer)

        return final_solution