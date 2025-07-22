# Workflow ID: hotpotqa_411_0
# Benchmark: hotpotqa
# Data Indices: [301, 3051, 820, 2012, 118]

class Workflow:
    def __init__(
        self,
        config,
        problem
    ) -> None:
        self.problem = problem
        self.config = create(config)
        self.flexible_custom = operator.FlexibleCustom(self.config, self.problem)
        self.custom = operator.Custom(self.config, self.problem)
        self.review = operator.Review(self.config, self.problem)
        self.sc_ensemble = operator.ScEnsemble(self.config, self.problem)

    async def run_workflow(self):
        """
        This is a workflow graph for multi-hop question answering.
        It uses FlexibleCustom for sequential reasoning to extract and connect facts,
        then Custom to synthesize the answer, and Review to validate it.
        Finally, ScEnsemble ensures robustness by selecting the best solution from multiple attempts.
        """
        # Step 1: Use FlexibleCustom with sequential reasoning to break down and connect information
        reasoning_path = await self.flexible_custom(
            custom_instruction="Break down the problem step-by-step, identify key entities, and trace connections between them.",
            reasoning_pattern="sequential",
            steps=["identify_entities", "find_connections", "trace_reasoning_path", "synthesize_answer"]
        )

        # Step 2: Use Custom to generate a clear, structured synthesis based on the reasoning path
        synthesized_answer = await self.custom(
            instruction="Based on the reasoning path, generate a concise and accurate answer with clear justification."
        )

        # Step 3: Use Review to critically assess the synthesized answer and refine it
        reviewed_answer = await self.review(pre_solution=synthesized_answer)

        # Step 4: Ensemble multiple solutions (simulate variation via a loop) for robustness
        solutions = [reviewed_answer]
        for _ in range(2):  # Generate 2 additional variations using different instructions
            variation = await self.custom(instruction="Solve this step-by-step with detailed logical reasoning.")
            solutions.append(variation)

        # Step 5: Select the best solution using ScEnsemble
        final_answer = await self.sc_ensemble(solutions=solutions)

        return final_answer