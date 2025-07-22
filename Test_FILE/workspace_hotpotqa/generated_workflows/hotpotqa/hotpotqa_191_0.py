# Workflow ID: hotpotqa_191_0
# Benchmark: hotpotqa
# Data Indices: [1342, 3197, 3141, 2011]

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
        It uses FlexibleCustom with sequential reasoning to break down the problem into steps.
        """
        # Step 1: Use FlexibleCustom for structured multi-hop reasoning
        solution = await self.flexible_custom(
            custom_instruction="Break down the problem step by step, identifying key entities and connections between them.",
            reasoning_pattern="sequential",
            steps=["extract_entities", "find_connections", "trace_reasoning_path", "synthesize_answer"]
        )

        # Step 2: Optionally refine using Review if needed (e.g., if initial solution lacks clarity)
        refined_solution = await self.review(pre_solution=solution)

        # Step 3: Generate final answer using AnswerGenerate as a safeguard
        final_answer = await self.answer_generate()

        # Step 4: Ensemble to ensure robustness — use both original and refined solutions
        ensemble_result = await self.sc_ensemble(solutions=[solution, refined_solution, final_answer])

        return ensemble_result