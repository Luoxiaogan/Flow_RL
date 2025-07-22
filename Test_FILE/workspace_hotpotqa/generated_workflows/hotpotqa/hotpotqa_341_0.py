# Workflow ID: hotpotqa_341_0
# Benchmark: hotpotqa
# Data Indices: [3533, 2806, 1923, 5, 3753]

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
        This is a workflow graph for multi-hop question answering using sequential reasoning.
        """
        # Step 1: Break down the problem into smaller steps with detailed reasoning
        step_by_step_reasoning = await self.custom(
            instruction="Can you solve this problem by breaking it down into detailed steps and explaining the reasoning behind each step?"
        )

        # Step 2: Use FlexibleCustom with sequential reasoning to trace multi-hop connections
        multi_hop_solution = await self.flexible_custom(
            custom_instruction="Focus on connecting information across different parts of the context",
            reasoning_pattern="sequential",
            steps=["identify_entities", "find_connections", "trace_reasoning_path", "synthesize_answer"]
        )

        # Step 3: Generate a direct answer as a baseline
        direct_answer = await self.answer_generate()

        # Step 4: Review the flexible custom solution to refine it
        refined_solution = await self.review(pre_solution=multi_hop_solution)

        # Step 5: Ensemble the solutions from multiple approaches for better accuracy
        solutions = [step_by_step_reasoning, multi_hop_solution, direct_answer, refined_solution]
        final_answer = await self.sc_ensemble(solutions=solutions)

        return final_answer