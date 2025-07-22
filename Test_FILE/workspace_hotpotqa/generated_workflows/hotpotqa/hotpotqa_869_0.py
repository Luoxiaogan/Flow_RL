# Workflow ID: hotpotqa_869_0
# Benchmark: hotpotqa
# Data Indices: [2419, 137, 2895, 106, 1552]

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
        It traces connections step-by-step through the context to solve complex problems.
        """
        # Step 1: Use FlexibleCustom with sequential reasoning to break down and trace multi-hop connections
        solution_step1 = await self.flexible_custom(
            custom_instruction="Break down the problem into smaller steps and trace connections between pieces of information in the context.",
            reasoning_pattern="sequential",
            steps=["identify_key_entities", "find_intermediate_connections", "trace_reasoning_path", "synthesize_answer"]
        )

        # Step 2: Generate an initial answer based on the structured reasoning
        solution_step2 = await self.answer_generate()

        # Step 3: Review the initial solution to improve accuracy
        reviewed_solution = await self.review(pre_solution=solution_step2)

        # Step 4: Ensemble multiple solutions (including original and reviewed) to select the best one
        solutions = [solution_step1, reviewed_solution]
        final_answer = await self.sc_ensemble(solutions=solutions)

        return final_answer