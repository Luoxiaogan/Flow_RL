# Workflow ID: hotpotqa_549_0
# Benchmark: hotpotqa
# Data Indices: [2108, 726, 173, 2512, 2754]

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
        It uses FlexibleCustom with sequential reasoning to break down the problem step-by-step.
        """
        # Step 1: Use flexible custom to extract entities and identify key connections
        solution1 = await self.flexible_custom(
            custom_instruction="Break down the problem into smaller steps by first identifying key entities and then finding logical connections between them.",
            reasoning_pattern="sequential",
            steps=["extract_entities", "find_connections", "trace_reasoning_path", "synthesize_answer"]
        )

        # Step 2: Generate an answer using direct reasoning (baseline)
        solution2 = await self.answer_generate()

        # Step 3: Review the initial solution to refine it
        reviewed_solution = await self.review(pre_solution=solution1)

        # Step 4: Ensemble the two solutions to get the best one
        final_solution = await self.sc_ensemble(solutions=[solution2, reviewed_solution])

        return final_solution