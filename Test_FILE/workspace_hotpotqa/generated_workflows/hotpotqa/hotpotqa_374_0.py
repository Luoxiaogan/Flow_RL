# Workflow ID: hotpotqa_374_0
# Benchmark: hotpotqa
# Data Indices: [1985, 309, 3138, 3199, 2471]

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
        It uses flexible custom for step-by-step reasoning, then synthesizes with custom,
        and validates with review to ensure accuracy.
        """
        # Step 1: Use FlexibleCustom with sequential reasoning to extract and connect facts
        solution_1 = await self.flexible_custom(
            custom_instruction="Break down the problem into smaller steps and explain the reasoning behind each step",
            reasoning_pattern="sequential",
            steps=["identify_key_entities", "find_intermediate_connections", "trace_reasoning_path", "synthesize_answer"]
        )

        # Step 2: Generate an initial answer using direct generation
        solution_2 = await self.answer_generate()

        # Step 3: Synthesize the results from flexible custom and direct generation
        synthesis_prompt = "Combine the following two solutions into one coherent and accurate answer:\n\nSolution 1:\n{}\n\nSolution 2:\n{}".format(solution_1, solution_2)
        solution_3 = await self.custom(instruction=synthesis_prompt)

        # Step 4: Review the synthesized answer for consistency and correctness
        final_solution = await self.review(pre_solution=solution_3)

        return final_solution