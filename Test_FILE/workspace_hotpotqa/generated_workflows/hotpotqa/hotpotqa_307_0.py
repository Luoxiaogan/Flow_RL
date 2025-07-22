# Workflow ID: hotpotqa_307_0
# Benchmark: hotpotqa
# Data Indices: [1049, 3062, 1955, 2321, 3770]

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
        It uses flexible custom reasoning to break down the problem into steps: extract_entities, find_connections, synthesize_answer.
        """
        # Step 1: Use FlexibleCustom with sequential reasoning to decompose and reason through the problem
        solution = await self.flexible_custom(
            custom_instruction="Break down the problem step by step using extraction, connection finding, and synthesis.",
            reasoning_pattern="sequential",
            steps=["extract_entities", "find_connections", "synthesize_answer"]
        )

        # Step 2: Generate a direct answer as a baseline (for ensemble)
        direct_answer = await self.answer_generate()

        # Step 3: Review the flexible custom solution to refine it
        reviewed_solution = await self.review(pre_solution=solution)

        # Step 4: Ensemble the direct answer and the reviewed solution
        final_solution = await self.sc_ensemble(solutions=[direct_answer, reviewed_solution])

        return final_solution