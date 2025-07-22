# Workflow ID: hotpotqa_416_0
# Benchmark: hotpotqa
# Data Indices: [3884, 1773, 2001, 419, 2394]

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
        then Custom to synthesize the answer, followed by Review for validation.
        Finally, ScEnsemble ensures the best solution from multiple attempts.
        """
        # Step 1: Use FlexibleCustom with sequential reasoning to break down the problem
        reasoning_steps = [
            "identify key entities and concepts",
            "find intermediate connections between entities",
            "trace the logical path from given information to the final answer",
            "synthesize the final answer"
        ]
        multi_hop_solution = await self.flexible_custom(
            custom_instruction="Break down the problem step-by-step, connecting facts logically.",
            reasoning_pattern="sequential",
            steps=reasoning_steps
        )

        # Step 2: Use Custom to refine and structure the solution based on the multi-hop reasoning
        refined_solution = await self.custom(
            instruction="Based on the multi-hop reasoning above, generate a clear and structured answer with proper justification."
        )

        # Step 3: Use Review to validate and improve the refined solution
        validated_solution = await self.review(pre_solution=refined_solution)

        # Step 4: Ensemble multiple solutions (simulate variation by generating a few via Custom)
        solutions = [
            await self.custom(instruction="Solve this step-by-step using detailed reasoning."),
            await self.custom(instruction="Explain your reasoning clearly and derive the answer from first principles."),
            validated_solution  # include the reviewed version as one of the ensemble candidates
        ]
        final_answer = await self.sc_ensemble(solutions=solutions)

        return final_answer