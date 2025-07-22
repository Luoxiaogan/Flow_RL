# Workflow ID: hotpotqa_877_0
# Benchmark: hotpotqa
# Data Indices: [13, 922, 3853, 1876, 1612]

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
        """
        # Step 1: Use FlexibleCustom to break down the problem into smaller steps with structured reasoning
        solution_step1 = await self.flexible_custom(
            custom_instruction="Break down the problem step-by-step and trace connections between pieces of information.",
            reasoning_pattern="sequential",
            steps=["identify_key_entities", "find_intermediate_connections", "trace_reasoning_path", "synthesize_final_answer"]
        )

        # Step 2: Generate an initial answer based on the structured breakdown
        solution_step2 = await self.answer_generate()

        # Step 3: Review the initial answer to refine it based on logical consistency
        reviewed_solution = await self.review(pre_solution=solution_step2)

        # Step 4: Ensembling multiple solutions improves robustness — generate two different answers via Custom
        solution1 = await self.custom(instruction="Solve this problem by breaking it down into detailed steps and explaining the reasoning behind each step.")
        solution2 = await self.custom(instruction="Explain how to solve the problem with clear reasoning for each step.")

        # Ensemble the two solutions to get a more reliable result
        final_solution = await self.sc_ensemble(solutions=[solution1, solution2, reviewed_solution])

        return final_solution