# Workflow ID: hotpotqa_423_0
# Benchmark: hotpotqa
# Data Indices: [1430, 804, 3320, 3294, 1614]

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
        It uses flexible custom for step-by-step reasoning, then synthesizes with Custom,
        ensembles multiple solutions if needed, and finally reviews to validate the answer.
        """
        # Step 1: Use FlexibleCustom with sequential reasoning to break down the problem
        reasoning_steps = [
            "identify key entities in the question",
            "find relevant facts from context",
            "connect intermediate pieces of information",
            "synthesize the final answer"
        ]
        multi_hop_solution = await self.flexible_custom(
            custom_instruction="Break down the problem into smaller steps and explain each reasoning step clearly.",
            reasoning_pattern="sequential",
            steps=reasoning_steps
        )

        # Step 2: Use Custom to synthesize the solution into a coherent answer
        synthesis = await self.custom(instruction="Based on the detailed reasoning above, generate a clear and concise final answer.")

        # Step 3: Ensemble with alternative reasoning paths (simulate multiple attempts)
        alternative_solutions = []
        for _ in range(2):  # Generate two alternative solutions via Custom with different prompts
            alt_sol = await self.custom(instruction="Solve this by first identifying the main topic, then extracting supporting facts, and finally combining them logically.")
            alternative_solutions.append(alt_sol)
        
        # Add original solution to ensemble list
        alternative_solutions.append(synthesis)

        # Step 4: Ensembling to select the best solution
        final_answer = await self.sc_ensemble(solutions=alternative_solutions)

        # Step 5: Review to validate the final answer
        validated_answer = await self.review(pre_solution=final_answer)

        return validated_answer