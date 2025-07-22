# Workflow ID: hotpotqa_144_0
# Benchmark: hotpotqa
# Data Indices: [3349, 3603, 321, 501]

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
        It uses flexible custom reasoning to break down the problem step-by-step,
        then synthesizes the answer using an ensemble of solutions for robustness.
        """
        # Step 1: Use FlexibleCustom with structured multi-hop steps to reason through the problem
        solution = await self.flexible_custom(
            custom_instruction="Break down the problem into smaller steps and explain the reasoning behind each step.",
            reasoning_pattern="sequential",
            steps=["extract_entities", "find_connections", "trace_reasoning_path", "synthesize_answer"]
        )

        # Step 2: Generate a direct answer as a baseline
        baseline_answer = await self.answer_generate()

        # Step 3: Ensemble the flexible custom solution and the baseline to improve accuracy
        solutions = [solution, baseline_answer]
        final_answer = await self.sc_ensemble(solutions=solutions)

        return final_answer