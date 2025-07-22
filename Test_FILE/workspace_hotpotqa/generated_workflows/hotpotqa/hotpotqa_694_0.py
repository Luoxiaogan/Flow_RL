# Workflow ID: hotpotqa_694_0
# Benchmark: hotpotqa
# Data Indices: [1624, 2650, 3586, 1640]

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
        It uses flexible custom for sequential reasoning to extract and connect facts,
        then synthesizes the answer using a custom instruction, and finally validates it via review.
        """
        # Step 1: Use FlexibleCustom with sequential reasoning to break down and connect information
        solution_1 = await self.flexible_custom(
            custom_instruction="Break down the problem into smaller steps and explain the reasoning behind each step.",
            reasoning_pattern="sequential",
            steps=["identify_key_entities", "extract_relevant_facts", "connect_information", "synthesize_answer"]
        )

        # Step 2: Generate a direct answer (for ensemble diversity)
        solution_2 = await self.answer_generate()

        # Step 3: Synthesize using Custom with step-by-step reasoning to reinforce clarity
        solution_3 = await self.custom(instruction="Solve this by breaking it down into detailed steps and explaining the reasoning behind each step.")

        # Step 4: Ensemble the three solutions to select the best one
        ensemble_solution = await self.sc_ensemble(solutions=[solution_1, solution_2, solution_3])

        # Step 5: Review the ensembled solution to refine and validate
        final_solution = await self.review(pre_solution=ensemble_solution)

        return final_solution