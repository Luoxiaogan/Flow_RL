# Workflow ID: hotpotqa_35_0
# Benchmark: hotpotqa
# Data Indices: [706, 607, 270, 3500]

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
        # Step 1: Generate initial answer using direct generation
        direct_answer = await self.answer_generate()

        # Step 2: Use flexible custom with sequential reasoning to break down the problem
        sequential_solution = await self.flexible_custom(
            custom_instruction="Break down the problem into smaller steps and reason step-by-step.",
            reasoning_pattern="sequential",
            steps=["identify_key_entities", "find_intermediate_connections", "trace_logical_path", "synthesize_final_answer"]
        )

        # Step 3: Use flexible custom with iterative refinement for accuracy
        iterative_solution = await self.flexible_custom(
            custom_instruction="Start with an initial hypothesis and refine it by checking facts and logic.",
            reasoning_pattern="iterative",
            steps=["initial_hypothesis", "verify_facts", "refine_answer"],
            max_iterations=3
        )

        # Step 4: Use a custom agent with step-by-step instruction to generate another path
        step_by_step_solution = await self.custom(
            instruction="Can you solve this problem by breaking it down into detailed steps and explaining the reasoning behind each step?"
        )

        # Step 5: Ensemble all solutions to select the best one
        solutions = [direct_answer, sequential_solution, iterative_solution, step_by_step_solution]
        ensembled_solution = await self.sc_ensemble(solutions=solutions)

        # Step 6: Final review to verify the selected solution
        final_answer = await self.review(pre_solution=ensembled_solution)

        return final_answer