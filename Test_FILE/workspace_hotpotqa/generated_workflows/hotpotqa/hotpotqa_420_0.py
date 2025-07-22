# Workflow ID: hotpotqa_420_0
# Benchmark: hotpotqa
# Data Indices: [3129, 3979, 81, 807]

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
        This is a robust workflow graph for multi-hop question answering.
        It uses multiple reasoning paths and ensemble to improve accuracy.
        """
        # Step 1: Generate initial answer using direct generation
        direct_answer = await self.answer_generate()

        # Step 2: Use flexible custom with sequential reasoning for structured multi-hop breakdown
        seq_solution = await self.flexible_custom(
            custom_instruction="Break down the problem into clear, logical steps and explain each step in detail.",
            reasoning_pattern="sequential",
            steps=["identify_key_entities", "find_intermediate_connections", "trace_reasoning_path", "synthesize_final_answer"]
        )

        # Step 3: Use flexible custom with iterative refinement for fact-checking and improvement
        iter_solution = await self.flexible_custom(
            custom_instruction="Start with an initial hypothesis, then verify facts and refine your answer progressively.",
            reasoning_pattern="iterative",
            steps=["initial_hypothesis", "verify_facts", "refine_answer"],
            max_iterations=3
        )

        # Step 4: Use Custom with step-by-step instruction for alternative reasoning path
        step_by_step = await self.custom(
            instruction="Solve this by breaking it down into smaller steps, explaining the reasoning behind each step."
        )

        # Step 5: Ensemble all solutions to select the best one
        solutions = [direct_answer, seq_solution, iter_solution, step_by_step]
        final_answer = await self.sc_ensemble(solutions=solutions)

        # Step 6: Final review to ensure correctness and clarity
        reviewed_answer = await self.review(pre_solution=final_answer)

        return reviewed_answer