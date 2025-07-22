# Workflow ID: hotpotqa_635_0
# Benchmark: hotpotqa
# Data Indices: [3545, 1068, 628, 874]

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
        This is a streamlined workflow graph for multi-hop question answering.
        Uses FlexibleCustom with sequential reasoning to break down complex problems step-by-step.
        """
        # Step 1: Use flexible custom to extract key entities and connections in a structured way
        solution = await self.flexible_custom(
            custom_instruction="Break down the problem into key entities and relationships step by step.",
            reasoning_pattern="sequential",
            steps=["extract_entities", "find_connections", "trace_reasoning_path", "synthesize_answer"]
        )

        # Step 2: Review the generated solution to refine reasoning if needed
        reviewed_solution = await self.review(pre_solution=solution)

        # Step 3: Generate final answer using the refined solution
        final_answer = await self.answer_generate()

        return final_answer