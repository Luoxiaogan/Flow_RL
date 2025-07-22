# Workflow ID: hotpotqa_475_0
# Benchmark: hotpotqa
# Data Indices: [1341, 2090, 1275, 1529, 2233]

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
        # Step 1: Use FlexibleCustom to trace multi-hop connections step-by-step
        solution = await self.flexible_custom(
            custom_instruction="Break down the problem into smaller steps and explain reasoning for each step",
            reasoning_pattern="sequential",
            steps=["identify_key_entities", "find_intermediate_connections", "trace_reasoning_path", "synthesize_final_answer"]
        )

        # Step 2: Review the generated solution for accuracy
        reviewed_solution = await self.review(pre_solution=solution)

        # Step 3: Generate final answer using direct generation as a fallback or verification
        final_answer = await self.answer_generate()

        # Step 4: Ensemble the original solution and the reviewed one to improve robustness
        ensemble_output = await self.sc_ensemble(solutions=[solution, reviewed_solution, final_answer])

        return ensemble_output