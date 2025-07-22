# Workflow ID: hotpotqa_312_0
# Benchmark: hotpotqa
# Data Indices: [644, 803, 1966, 2450, 3775]

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
        then synthesizes the answer based on extracted entities and connections.
        """
        # Step 1: Use FlexibleCustom with sequential reasoning to extract key entities and trace connections
        solution = await self.flexible_custom(
            custom_instruction="Break down the problem step by step, identify key entities, and trace logical connections between them.",
            reasoning_pattern="sequential",
            steps=["extract_entities", "find_connections", "trace_reasoning_path", "synthesize_answer"]
        )

        # Step 2: Generate an answer using direct generation as a baseline
        baseline_answer = await self.answer_generate()

        # Step 3: Ensemble the flexible custom result with the baseline to improve robustness
        solutions = [solution, baseline_answer]
        final_solution = await self.sc_ensemble(solutions=solutions)

        return final_solution