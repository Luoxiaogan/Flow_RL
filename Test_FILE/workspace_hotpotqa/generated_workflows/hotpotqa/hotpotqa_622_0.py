# Workflow ID: hotpotqa_622_0
# Benchmark: hotpotqa
# Data Indices: [816, 3067, 2957, 1104, 3135]

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
        It uses multiple reasoning paths and ensemble to improve accuracy.
        """
        # Step 1: Generate initial answer using direct generation
        direct_answer = await self.answer_generate()

        # Step 2: Generate step-by-step reasoning using Custom
        step_by_step = await self.custom(instruction="Can you solve this problem by breaking it down into detailed steps and explaining the reasoning behind each step?")

        # Step 3: Use FlexibleCustom for iterative refinement (multi-hop reasoning)
        refined_answer = await self.flexible_custom(
            custom_instruction="Focus on connecting information across different parts of the context",
            reasoning_pattern="iterative",
            steps=["identify_entities", "find_connections", "trace_reasoning_path", "synthesize_answer"],
            max_iterations=2
        )

        # Step 4: Create a list of solutions for ensemble
        solutions = [direct_answer, step_by_step, refined_answer]

        # Step 5: Ensemble the solutions to select the best one
        ensembled_solution = await self.sc_ensemble(solutions=solutions)

        # Step 6: Final review to verify and refine if needed
        final_answer = await self.review(pre_solution=ensembled_solution)

        return final_answer