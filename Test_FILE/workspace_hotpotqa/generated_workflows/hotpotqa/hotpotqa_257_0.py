# Workflow ID: hotpotqa_257_0
# Benchmark: hotpotqa
# Data Indices: [2565, 1599, 3964, 3585]

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
        It breaks down the problem into steps, traces connections across context, and refines the answer.
        """
        # Step 1: Use FlexibleCustom with sequential multi-hop reasoning to trace connections
        solution = await self.flexible_custom(
            custom_instruction="Break down the problem step-by-step, identify key entities, find connections between them, and trace the reasoning path to derive the final answer.",
            reasoning_pattern="sequential",
            steps=["identify_entities", "find_connections", "trace_reasoning_path", "synthesize_answer"]
        )

        # Step 2: Review the initial solution for potential errors or missing logic
        reviewed_solution = await self.review(pre_solution=solution)

        # Step 3: Generate an independent answer directly from the problem (as a baseline)
        direct_answer = await self.answer_generate()

        # Step 4: Ensemble both the reviewed solution and the direct answer to improve robustness
        ensemble_solution = await self.sc_ensemble(solutions=[reviewed_solution, direct_answer])

        return ensemble_solution