# Workflow ID: hotpotqa_805_0
# Benchmark: hotpotqa
# Data Indices: [2518, 638, 2486, 1771]

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
        # Step 1: Generate initial answer directly
        direct_answer = await self.answer_generate()

        # Step 2: Use Custom to break down the problem into steps
        step_by_step = await self.custom(instruction="Can you solve this problem by breaking it down into detailed steps and explaining the reasoning behind each step?")

        # Step 3: Use FlexibleCustom with sequential reasoning for structured multi-hop path
        sequential_reasoning = await self.flexible_custom(
            custom_instruction="Focus on connecting information across different parts of the context",
            reasoning_pattern="sequential",
            steps=["identify_entities", "find_connections", "trace_reasoning_path", "synthesize_answer"]
        )

        # Step 4: Use FlexibleCustom with iterative refinement for accuracy
        iterative_refinement = await self.flexible_custom(
            custom_instruction="Start with an initial answer and refine it through fact-checking and logical verification",
            reasoning_pattern="iterative",
            steps=["initial_hypothesis", "verify_facts", "refine_answer"],
            max_iterations=3
        )

        # Step 5: Ensemble the three solutions
        solutions = [direct_answer, step_by_step, sequential_reasoning, iterative_refinement]
        final_solution = await self.sc_ensemble(solutions=solutions)

        # Step 6: Final review to ensure correctness and coherence
        final_answer = await self.review(pre_solution=final_solution)

        return final_answer