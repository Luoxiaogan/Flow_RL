# Workflow ID: hotpotqa_783_0
# Benchmark: hotpotqa
# Data Indices: [944, 1231, 398, 2285, 1376]

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
        It uses FlexibleCustom with sequential reasoning to break down complex problems.
        """
        # Step 1: Use flexible custom to extract key entities and find connections
        solution = await self.flexible_custom(
            custom_instruction="Break the problem into smaller steps and trace connections between entities.",
            reasoning_pattern="sequential",
            steps=["extract_entities", "find_connections", "trace_reasoning_path", "synthesize_answer"]
        )

        # Step 2: Optionally refine using review if needed
        refined_solution = await self.review(pre_solution=solution)

        # Step 3: Generate final answer using ensemble of multiple approaches
        # We generate two different solutions via Custom (with slightly different prompts) for diversity
        solution1 = await self.custom(instruction="Solve this by breaking it into clear, logical steps.")
        solution2 = await self.custom(instruction="First identify all relevant facts, then reason step-by-step.")

        # Ensemble the solutions to improve accuracy
        final_answer = await self.sc_ensemble(solutions=[refined_solution, solution1, solution2])

        return final_answer