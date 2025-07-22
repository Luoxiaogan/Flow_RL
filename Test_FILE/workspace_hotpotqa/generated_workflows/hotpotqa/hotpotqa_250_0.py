# Workflow ID: hotpotqa_250_0
# Benchmark: hotpotqa
# Data Indices: [337, 354, 1141, 3038, 466]

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
        Uses FlexibleCustom with sequential reasoning to extract entities, find connections, and synthesize answer.
        """
        # Step 1: Use flexible custom to break down the problem in a structured way
        solution = await self.flexible_custom(
            custom_instruction="Break down the problem step-by-step by first extracting key entities, then finding logical connections between them, and finally synthesizing a coherent answer.",
            reasoning_pattern="sequential",
            steps=["extract_entities", "find_connections", "synthesize_answer"]
        )
        
        # Step 2: Review the generated solution to refine it
        reviewed_solution = await self.review(pre_solution=solution)
        
        # Step 3: Generate a final answer based on the reviewed solution
        final_answer = await self.answer_generate()
        
        return final_answer