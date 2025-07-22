# Workflow ID: hotpotqa_231_0
# Benchmark: hotpotqa
# Data Indices: [3948, 1533, 847, 3412, 3610]

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
        It breaks down the problem into steps, traces connections across sources, and ensembles solutions.
        """
        # Step 1: Use FlexibleCustom with sequential reasoning to trace multi-hop connections
        solution_1 = await self.flexible_custom(
            custom_instruction="Break down the problem step-by-step, identifying key entities and connections between them.",
            reasoning_pattern="sequential",
            steps=["identify_entities", "find_connections", "trace_reasoning_path", "synthesize_answer"]
        )

        # Step 2: Generate an answer directly (baseline)
        solution_2 = await self.answer_generate()

        # Step 3: Review the direct answer to improve it
        reviewed_solution = await self.review(pre_solution=solution_2)

        # Step 4: Ensemble the two solutions (original flexible custom + reviewed answer)
        ensemble_solution = await self.sc_ensemble(solutions=[solution_1, reviewed_solution])

        return ensemble_solution