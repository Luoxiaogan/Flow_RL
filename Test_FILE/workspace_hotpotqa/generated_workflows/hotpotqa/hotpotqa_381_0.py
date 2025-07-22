# Workflow ID: hotpotqa_381_0
# Benchmark: hotpotqa
# Data Indices: [3815, 3754, 1326, 1806, 3953]

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
        It uses sequential reasoning to extract and connect facts, then synthesizes the answer and validates it.
        """
        # Step 1: Use FlexibleCustom with sequential reasoning to break down the problem and extract key facts
        reasoning_solution = await self.flexible_custom(
            custom_instruction="Break down the problem step-by-step and extract relevant facts from the context.",
            reasoning_pattern="sequential",
            steps=["identify_key_entities", "extract_facts", "connect_information", "synthesize_answer"]
        )

        # Step 2: Use Custom to synthesize a clear and logical answer based on the extracted facts
        synthesis_solution = await self.custom(instruction="Based on the extracted facts, generate a clear and concise answer with reasoning.")

        # Step 3: Ensembling multiple solutions (here we use the two above) to improve robustness
        ensemble_solution = await self.sc_ensemble(solutions=[reasoning_solution, synthesis_solution])

        # Step 4: Review the final solution to ensure accuracy and completeness
        final_answer = await self.review(pre_solution=ensemble_solution)

        return final_answer