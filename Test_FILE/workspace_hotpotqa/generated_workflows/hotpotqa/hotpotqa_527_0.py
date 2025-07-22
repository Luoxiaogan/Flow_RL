# Workflow ID: hotpotqa_527_0
# Benchmark: hotpotqa
# Data Indices: [1824, 3879, 3351, 95, 1764]

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
        Uses FlexibleCustom with structured reasoning steps to break down complex questions.
        """
        # Step 1: Use FlexibleCustom to extract entities and key concepts from the problem
        step1_solution = await self.flexible_custom(
            custom_instruction="Break down the problem into core entities and relationships.",
            reasoning_pattern="sequential",
            steps=["extract_entities", "find_connections", "trace_reasoning_path"]
        )

        # Step 2: Generate an answer based on the structured reasoning
        step2_answer = await self.answer_generate()

        # Step 3: Review the generated answer using the structured reasoning as context
        reviewed_answer = await self.review(pre_solution=step2_answer)

        # Step 4: Ensemble multiple solutions (including original and reviewed) for robustness
        solutions = [step2_answer, reviewed_answer]
        final_answer = await self.sc_ensemble(solutions=solutions)

        return final_answer