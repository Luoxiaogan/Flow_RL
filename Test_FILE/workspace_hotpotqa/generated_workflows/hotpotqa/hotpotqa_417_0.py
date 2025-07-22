# Workflow ID: hotpotqa_417_0
# Benchmark: hotpotqa
# Data Indices: [386, 574, 3630, 2708]

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
        self.sc_ensemble = operator.ScEnsemble(self.config, self.problem)
        self.review = operator.Review(self.config, self.problem)

    async def run_workflow(self):
        """
        This is a workflow graph for multi-hop question answering.
        It uses FlexibleCustom for sequential reasoning to extract and connect facts,
        then Custom for synthesis, followed by Review for validation, and finally ensembles
        with ScEnsemble to ensure robustness.
        """
        # Step 1: Use FlexibleCustom with sequential reasoning to break down the problem
        # into steps like identifying entities, finding connections, tracing paths, and synthesizing
        reasoning_solution = await self.flexible_custom(
            custom_instruction="Break down the problem step-by-step using sequential reasoning to identify key facts and their relationships.",
            reasoning_pattern="sequential",
            steps=["identify_entities", "find_connections", "trace_reasoning_path", "synthesize_answer"]
        )

        # Step 2: Use Custom to synthesize a clear answer based on the structured reasoning
        synthesized_answer = await self.custom(
            instruction="Based on the structured reasoning above, generate a concise and accurate final answer."
        )

        # Step 3: Review the synthesized answer to catch potential errors or omissions
        reviewed_answer = await self.review(pre_solution=synthesized_answer)

        # Step 4: Ensembling to improve robustness — include both original and reviewed answers
        ensemble_solution = await self.sc_ensemble(solutions=[synthesized_answer, reviewed_answer])

        return ensemble_solution