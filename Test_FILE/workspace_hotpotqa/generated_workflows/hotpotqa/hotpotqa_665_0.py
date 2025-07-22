# Workflow ID: hotpotqa_665_0
# Benchmark: hotpotqa
# Data Indices: [3493, 2824, 2213, 1671]

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
        Uses FlexibleCustom for structured multi-hop reasoning and ensembles solutions for robustness.
        """
        # Step 1: Use FlexibleCustom to systematically break down the problem into entities, connections, and synthesis
        multi_hop_solution = await self.flexible_custom(
            custom_instruction="Break down the problem step-by-step by first extracting key entities, then identifying logical connections between them, and finally synthesizing a coherent answer.",
            reasoning_pattern="sequential",
            steps=["extract_entities", "find_connections", "synthesize_answer"]
        )

        # Step 2: Generate a direct answer using AnswerGenerate as a baseline
        direct_answer = await self.answer_generate()

        # Step 3: Ensemble the two solutions to improve accuracy
        ensemble_result = await self.sc_ensemble(solutions=[multi_hop_solution, direct_answer])

        # Step 4: Review the ensemble result for clarity and correctness
        final_answer = await self.review(pre_solution=ensemble_result)

        return final_answer