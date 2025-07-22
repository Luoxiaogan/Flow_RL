# Workflow ID: hotpotqa_742_0
# Benchmark: hotpotqa
# Data Indices: [2417, 2402, 1320, 1569]

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
        It uses FlexibleCustom with sequential reasoning to break down the problem,
        then optionally refines the answer via review and ensembles multiple solutions.
        """
        # Step 1: Use flexible custom to extract entities and trace connections step-by-step
        solution = await self.flexible_custom(
            custom_instruction="Break down the problem into smaller steps and explain your reasoning.",
            reasoning_pattern="sequential",
            steps=["extract_entities", "find_connections", "trace_reasoning_path", "synthesize_answer"]
        )

        # Step 2: Optionally refine the solution using Review if needed
        refined_solution = await self.review(pre_solution=solution)

        # Step 3: Generate final answer using AnswerGenerate as a fallback or verification
        final_answer = await self.answer_generate()

        # Step 4: Ensemble the main solution and the refined one to improve accuracy
        ensemble_result = await self.sc_ensemble(solutions=[solution, refined_solution, final_answer])

        return ensemble_result