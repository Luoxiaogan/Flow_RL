# Workflow ID: hotpotqa_139_0
# Benchmark: hotpotqa
# Data Indices: [361, 3240, 206, 1327, 2893]

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
        Uses FlexibleCustom for structured multi-hop reasoning and ensembles solutions for robustness.
        """
        # Step 1: Use flexible custom to break down the problem into key steps (extract, connect, synthesize)
        multi_hop_solution = await self.flexible_custom(
            custom_instruction="Break down the problem step by step using multi-hop reasoning.",
            reasoning_pattern="sequential",
            steps=["extract_entities", "find_connections", "trace_reasoning_path", "synthesize_answer"]
        )

        # Step 2: Generate an answer directly as a baseline
        direct_answer = await self.answer_generate()

        # Step 3: Ensemble both solutions to improve accuracy
        solutions = [multi_hop_solution, direct_answer]
        final_answer = await self.sc_ensemble(solutions=solutions)

        return final_answer