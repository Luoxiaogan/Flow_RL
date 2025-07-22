# Workflow ID: hotpotqa_230_0
# Benchmark: hotpotqa
# Data Indices: [3341, 2721, 305, 317]

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
        It uses FlexibleCustom with sequential reasoning to break down the problem,
        then ensembles multiple solutions for robustness.
        """
        # Step 1: Use FlexibleCustom for structured multi-hop reasoning
        multi_hop_solution = await self.flexible_custom(
            custom_instruction="Break down the problem into smaller steps and reason step-by-step.",
            reasoning_pattern="sequential",
            steps=["extract_entities", "find_connections", "trace_reasoning_path", "synthesize_answer"]
        )

        # Step 2: Generate an answer directly as a baseline
        direct_answer = await self.answer_generate()

        # Step 3: Review the multi-hop solution for refinement
        reviewed_solution = await self.review(pre_solution=multi_hop_solution)

        # Step 4: Ensemble the direct answer and the reviewed solution
        ensemble_solution = await self.sc_ensemble(solutions=[direct_answer, reviewed_solution])

        return ensemble_solution