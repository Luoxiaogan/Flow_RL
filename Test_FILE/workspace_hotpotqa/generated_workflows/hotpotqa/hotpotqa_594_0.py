# Workflow ID: hotpotqa_594_0
# Benchmark: hotpotqa
# Data Indices: [703, 1727, 3176, 643]

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
        It breaks down the problem into smaller steps and connects information across different parts of the context.
        """
        # Step 1: Use FlexibleCustom with sequential reasoning to trace multi-hop connections
        solution = await self.flexible_custom(
            custom_instruction="Break down the problem step-by-step, identifying key entities and connections between them.",
            reasoning_pattern="sequential",
            steps=["identify_entities", "find_connections", "trace_reasoning_path", "synthesize_answer"]
        )

        # Step 2: Generate an answer directly as a baseline
        direct_answer = await self.answer_generate()

        # Step 3: Ensemble the flexible custom solution and direct answer
        solutions = [solution, direct_answer]
        ensembled_solution = await self.sc_ensemble(solutions=solutions)

        # Step 4: Review the ensembled solution to refine it
        final_solution = await self.review(pre_solution=ensembled_solution)

        return final_solution