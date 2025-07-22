# Workflow ID: hotpotqa_630_0
# Benchmark: hotpotqa
# Data Indices: [3647, 1386, 672, 3107]

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
        # Step 1: Use FlexibleCustom with sequential reasoning to break down the problem
        solution_1 = await self.flexible_custom(
            custom_instruction="Break down the problem into smaller steps and trace the connections between pieces of information in the context.",
            reasoning_pattern="sequential",
            steps=["identify_key_entities", "find_intermediate_connections", "trace_reasoning_path", "synthesize_final_answer"]
        )

        # Step 2: Generate an answer directly as a baseline
        solution_2 = await self.answer_generate()

        # Step 3: Review the initial solution to refine it
        reviewed_solution = await self.review(pre_solution=solution_1)

        # Step 4: Ensemble the two solutions (original flexible custom and reviewed) to improve robustness
        ensemble_solution = await self.sc_ensemble(solutions=[solution_1, reviewed_solution, solution_2])

        return ensemble_solution