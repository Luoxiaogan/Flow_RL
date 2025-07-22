# Workflow ID: hotpotqa_235_0
# Benchmark: hotpotqa
# Data Indices: [2620, 2740, 1680, 1481]

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
        then synthesizes an answer based on extracted entities and connections.
        """
        # Step 1: Use FlexibleCustom with sequential reasoning to extract key entities and find connections
        solution = await self.flexible_custom(
            custom_instruction="Break down the problem step-by-step by first extracting relevant entities, then identifying how they connect across different pieces of information.",
            reasoning_pattern="sequential",
            steps=["extract_entities", "find_connections", "trace_reasoning_path", "synthesize_answer"]
        )

        # Step 2: Optionally refine using Review if needed (e.g., if initial synthesis lacks clarity)
        refined_solution = await self.review(pre_solution=solution)

        # Step 3: Generate final answer directly from the refined solution
        final_answer = await self.answer_generate()

        return final_answer