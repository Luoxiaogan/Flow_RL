# Workflow ID: hotpotqa_482_0
# Benchmark: hotpotqa
# Data Indices: [64, 1868, 2125, 690, 2593]

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
        This is a streamlined workflow graph for multi-hop question answering.
        Uses FlexibleCustom with sequential reasoning to break down the problem into steps.
        """
        # Step 1: Use FlexibleCustom to extract entities and key facts from the problem
        solution_1 = await self.flexible_custom(
            custom_instruction="Break down the problem into smaller steps by identifying key entities and relationships.",
            reasoning_pattern="sequential",
            steps=["extract_entities", "find_connections", "trace_reasoning_path", "synthesize_answer"]
        )

        # Step 2: Generate an initial answer using direct reasoning
        solution_2 = await self.answer_generate()

        # Step 3: Review the initial answer to refine it based on context
        reviewed_solution = await self.review(pre_solution=solution_2)

        # Step 4: Ensemble the two solutions to improve robustness
        final_solution = await self.sc_ensemble(solutions=[solution_1, reviewed_solution])

        return final_solution