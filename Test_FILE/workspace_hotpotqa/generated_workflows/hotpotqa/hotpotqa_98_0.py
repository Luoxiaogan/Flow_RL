# Workflow ID: hotpotqa_98_0
# Benchmark: hotpotqa
# Data Indices: [3750, 3235, 3933, 482]

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
        then synthesizes an answer based on connections found across information sources.
        """
        # Step 1: Use FlexibleCustom for structured multi-hop reasoning
        solution = await self.flexible_custom(
            custom_instruction="Break down the problem step-by-step and trace logical connections between entities.",
            reasoning_pattern="sequential",
            steps=["extract_entities", "find_connections", "trace_reasoning_path", "synthesize_answer"]
        )

        # Step 2: Optionally refine with review if needed (e.g., for complex problems)
        refined_solution = await self.review(pre_solution=solution)

        # Step 3: Final ensemble of multiple solutions (if more than one exists)
        # Here we generate a few alternative paths using Custom with different instructions
        alt_solutions = [
            await self.custom(instruction="Solve this by identifying key entities and how they relate to each other."),
            await self.custom(instruction="Think through this in steps: first identify what is being asked, then find relevant facts, then connect them.")
        ]
        
        # Ensemble the original solution and alternatives
        final_solution = await self.sc_ensemble(solutions=[refined_solution] + alt_solutions)

        return final_solution