# Workflow ID: hotpotqa_466_0
# Benchmark: hotpotqa
# Data Indices: [3468, 1013, 930, 1081]

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
        It uses FlexibleCustom for structured reasoning and ensembles multiple solutions.
        """
        # Step 1: Use FlexibleCustom to extract entities and trace connections in a sequential manner
        solution_1 = await self.flexible_custom(
            custom_instruction="Break down the problem step by step using entity extraction, connection finding, and synthesis.",
            reasoning_pattern="sequential",
            steps=["extract_entities", "find_connections", "synthesize_answer"]
        )

        # Step 2: Generate a direct answer using AnswerGenerate for baseline comparison
        solution_2 = await self.answer_generate()

        # Step 3: Use Custom with a step-by-step instruction to generate an alternative reasoned solution
        solution_3 = await self.custom(instruction="Solve this problem by breaking it down into detailed steps and explaining the reasoning behind each step.")

        # Step 4: Ensemble all three solutions to select the best one
        ensemble_result = await self.sc_ensemble(solutions=[solution_1, solution_2, solution_3])

        # Step 5: Review the ensembled result to refine if necessary
        final_solution = await self.review(pre_solution=ensemble_result)

        return final_solution