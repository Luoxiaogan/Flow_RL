# Workflow ID: hotpotqa_766_0
# Benchmark: hotpotqa
# Data Indices: [2991, 1408, 1508, 1371, 516]

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
        It uses multiple reasoning paths to enhance robustness and accuracy.
        """
        # Step 1: Generate initial answer using direct generation
        direct_answer = await self.answer_generate()

        # Step 2: Use flexible custom with sequential reasoning for structured multi-hop thinking
        sequential_solution = await self.flexible_custom(
            custom_instruction="Break down the problem into smaller steps and explain each step clearly.",
            reasoning_pattern="sequential",
            steps=["identify_key_entities", "find_intermediate_connections", "trace_reasoning_path", "synthesize_final_answer"]
        )

        # Step 3: Generate alternative reasoning path using Custom with detailed step-by-step instruction
        step_by_step_solution = await self.custom(
            instruction="Solve this problem by breaking it down into detailed steps and explaining the reasoning behind each step."
        )

        # Step 4: Ensemble the three solutions to select the most consistent and well-supported one
        ensemble_input = [direct_answer, sequential_solution, step_by_step_solution]
        ensembled_answer = await self.sc_ensemble(solutions=ensemble_input)

        # Step 5: Final review to refine and validate the best solution
        final_answer = await self.review(pre_solution=ensembled_answer)

        return final_answer