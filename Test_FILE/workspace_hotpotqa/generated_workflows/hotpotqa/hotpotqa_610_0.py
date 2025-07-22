# Workflow ID: hotpotqa_610_0
# Benchmark: hotpotqa
# Data Indices: [626, 3329, 2098, 2804]

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
        It uses sequential reasoning to extract and connect facts, then synthesizes the answer with custom instruction.
        Finally, it validates the solution through review.
        """
        # Step 1: Use FlexibleCustom with sequential reasoning to break down the problem and extract relevant facts
        fact_extraction = await self.flexible_custom(
            custom_instruction="Break down the problem into smaller steps and identify key pieces of information needed to solve it.",
            reasoning_pattern="sequential",
            steps=["identify_question_components", "extract_facts", "find_connections", "trace_reasoning_path"]
        )

        # Step 2: Use Custom to synthesize a coherent answer based on extracted facts
        synthesis = await self.custom(instruction="Based on the extracted facts, generate a detailed step-by-step explanation leading to the final answer.")

        # Step 3: Review the synthesized answer to validate correctness and refine if necessary
        reviewed_answer = await self.review(pre_solution=synthesis)

        # Step 4: Ensemble multiple solutions (here just one) to ensure robustness
        ensemble_solution = await self.sc_ensemble(solutions=[reviewed_answer])

        return ensemble_solution