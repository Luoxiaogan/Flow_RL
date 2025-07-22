# Workflow ID: hotpotqa_70_0
# Benchmark: hotpotqa
# Data Indices: [1994, 2481, 1573, 3838]

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
        It uses flexible custom reasoning to break down the problem into steps,
        then synthesizes an answer based on extracted entities and connections.
        """
        # Step 1: Use FlexibleCustom to perform structured multi-hop reasoning
        solution = await self.flexible_custom(
            custom_instruction="Break down the problem step by step using multi-hop reasoning.",
            reasoning_pattern="sequential",
            steps=["extract_entities", "find_connections", "trace_reasoning_path", "synthesize_answer"]
        )

        # Step 2: Optionally refine with Review if needed (can be skipped if not necessary)
        refined_solution = await self.review(pre_solution=solution)

        # Step 3: Generate final answer using AnswerGenerate as a fallback or verification
        final_answer = await self.answer_generate()

        # Step 4: Ensemble the solutions to improve robustness
        ensemble_result = await self.sc_ensemble(solutions=[refined_solution, final_answer])

        return ensemble_result