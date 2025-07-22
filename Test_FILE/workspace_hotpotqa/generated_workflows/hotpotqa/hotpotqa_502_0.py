# Workflow ID: hotpotqa_502_0
# Benchmark: hotpotqa
# Data Indices: [1398, 2756, 3804, 3238]

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
        It uses multiple reasoning paths and ensemble to improve robustness.
        """
        # Step 1: Generate initial answer directly
        direct_answer = await self.answer_generate()

        # Step 2: Use flexible custom with sequential reasoning for step-by-step breakdown
        sequential_reasoning = await self.flexible_custom(
            custom_instruction="Break down the problem into smaller steps and explain the reasoning behind each step.",
            reasoning_pattern="sequential",
            steps=["identify_key_entities", "find_intermediate_connections", "trace_logical_path", "synthesize_final_answer"]
        )

        # Step 3: Use flexible custom with iterative refinement to improve answer quality
        iterative_refinement = await self.flexible_custom(
            custom_instruction="Start with an initial hypothesis, verify facts, and refine the answer iteratively.",
            reasoning_pattern="iterative",
            steps=["initial_hypothesis", "verify_evidence", "refine_answer"],
            max_iterations=3
        )

        # Step 4: Generate alternative solution using a different custom instruction (e.g., structured reasoning)
        structured_reasoning = await self.custom(
            instruction="Solve this by identifying all relevant entities, then connecting them logically through intermediate steps."
        )

        # Step 5: Ensemble the solutions from different reasoning paths
        solutions = [direct_answer, sequential_reasoning, iterative_refinement, structured_reasoning]
        ensembled_solution = await self.sc_ensemble(solutions=solutions)

        # Step 6: Final review to ensure coherence and correctness
        final_answer = await self.review(pre_solution=ensembled_solution)

        return final_answer