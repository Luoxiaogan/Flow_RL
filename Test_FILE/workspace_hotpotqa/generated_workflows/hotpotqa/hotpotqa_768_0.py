# Workflow ID: hotpotqa_768_0
# Benchmark: hotpotqa
# Data Indices: [492, 3040, 1412, 1536]

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
        It uses FlexibleCustom for structured multi-hop reasoning and ensembles solutions.
        """
        # Step 1: Use FlexibleCustom to break down the problem into entities, connections, and synthesis
        solution = await self.flexible_custom(
            custom_instruction="Break down the problem by extracting key entities, finding logical connections between them, and synthesizing a coherent answer.",
            reasoning_pattern="sequential",
            steps=["extract_entities", "find_connections", "synthesize_answer"]
        )

        # Step 2: Generate an answer using direct reasoning as a baseline
        baseline_answer = await self.answer_generate()

        # Step 3: Ensemble the flexible custom result with the baseline to improve robustness
        ensemble_solution = await self.sc_ensemble(solutions=[solution, baseline_answer])

        # Step 4: Review the ensemble solution for clarity and correctness
        final_answer = await self.review(pre_solution=ensemble_solution)

        return final_answer