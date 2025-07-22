# Workflow ID: hotpotqa_648_0
# Benchmark: hotpotqa
# Data Indices: [3166, 967, 796, 676]

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
        It breaks down the problem into steps, traces connections across context, and refines the answer.
        """
        # Step 1: Generate an initial answer with detailed reasoning
        initial_answer = await self.answer_generate()

        # Step 2: Use FlexibleCustom with sequential multi-hop reasoning to trace connections step-by-step
        multi_hop_solution = await self.flexible_custom(
            custom_instruction="Break down the problem into smaller steps and explain the reasoning behind each step.",
            reasoning_pattern="sequential",
            steps=["identify_entities", "find_connections", "trace_reasoning_path", "synthesize_answer"]
        )

        # Step 3: Review the initial answer using the multi-hop solution as context
        refined_answer = await self.review(pre_solution=initial_answer)

        # Step 4: Ensemble multiple solutions (including original and refined) for robustness
        solutions = [initial_answer, refined_answer, multi_hop_solution]
        final_answer = await self.sc_ensemble(solutions=solutions)

        return final_answer