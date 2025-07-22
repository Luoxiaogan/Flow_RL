# Workflow ID: hotpotqa_852_0
# Benchmark: hotpotqa
# Data Indices: [1497, 3223, 343, 2226, 2870]

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
        It uses sequential reasoning to extract and connect facts, then synthesizes the answer.
        Finally, it reviews the solution for accuracy.
        """
        # Step 1: Use FlexibleCustom with sequential reasoning to break down the problem
        # and trace connections between pieces of information across context.
        reasoning_path = await self.flexible_custom(
            custom_instruction="Break down the problem into smaller steps and trace the logical connections between entities and facts.",
            reasoning_pattern="sequential",
            steps=["identify_entities", "find_connections", "trace_reasoning_path", "synthesize_answer"]
        )

        # Step 2: Use Custom to synthesize the final answer based on the structured reasoning path.
        synthesis = await self.custom(
            instruction="Based on the step-by-step reasoning above, generate a clear and concise final answer."
        )

        # Step 3: Review the synthesized answer for correctness and clarity.
        reviewed_answer = await self.review(pre_solution=synthesis)

        # Optional: Ensembling multiple solutions can improve robustness.
        # Generate a few alternative solutions via Custom with different instructions.
        alt_solutions = [
            await self.custom(instruction="Solve this by focusing only on direct evidence from the context."),
            await self.custom(instruction="Solve this by identifying key clues first, then building the answer logically."),
            await self.custom(instruction="Solve this by considering what the question is really asking and why.")
        ]
        
        # Ensemble the main solution with alternatives to select the best one.
        final_answer = await self.sc_ensemble(solutions=[reviewed_answer] + alt_solutions)

        return final_answer