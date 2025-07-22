# Workflow ID: hotpotqa_94_0
# Benchmark: hotpotqa
# Data Indices: [2442, 1316, 1410, 2398]

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
        It uses FlexibleCustom with sequential reasoning to break down complex problems.
        """
        # Step 1: Use flexible custom to extract key entities and connections
        solution1 = await self.flexible_custom(
            custom_instruction="Break the problem into smaller steps by first identifying key entities and relationships.",
            reasoning_pattern="sequential",
            steps=["extract_entities", "find_connections", "trace_reasoning_path", "synthesize_answer"]
        )

        # Step 2: Generate a direct answer as a baseline
        solution2 = await self.answer_generate()

        # Step 3: Review the initial solution to refine it
        reviewed_solution = await self.review(pre_solution=solution1)

        # Step 4: Ensemble the two solutions (original flexible custom result and reviewed one)
        final_solution = await self.sc_ensemble(solutions=[solution1, reviewed_solution])

        return final_solution