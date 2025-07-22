# Workflow ID: hotpotqa_17_0
# Benchmark: hotpotqa
# Data Indices: [2316, 2314, 2908, 1491]

class Workflow:
    def __init__(
        self,
        config,
        problem
    ) -> None:
        self.problem = problem
        self.config = create(config)
        self.flexible_custom = operator.FlexibleCustom(self.config, self.problem)
        self.custom = operator.Custom(self.config, self.problem)
        self.sc_ensemble = operator.ScEnsemble(self.config, self.problem)
        self.review = operator.Review(self.config, self.problem)
        self.answer_generate = operator.AnswerGenerate(self.config, self.problem)

    async def run_workflow(self):
        """
        This is a workflow graph for multi-hop question answering.
        It uses flexible custom for sequential reasoning to extract and connect facts,
        then synthesizes the answer with a custom instruction, reviews it for accuracy,
        and finally ensembles multiple solutions if needed.
        """
        # Step 1: Use FlexibleCustom with sequential reasoning to break down and trace multi-hop logic
        reasoning_steps = [
            "identify_key_entities",
            "find_intermediate_connections",
            "trace_logical_path",
            "synthesize_final_answer"
        ]
        reasoning_solution = await self.flexible_custom(
            custom_instruction="Break down the problem step by step, identify key entities, and trace how they connect logically.",
            reasoning_pattern="sequential",
            steps=reasoning_steps
        )

        # Step 2: Generate an initial answer using Custom with step-by-step instruction
        initial_answer = await self.custom(
            instruction="Solve this problem by breaking it down into detailed steps and explaining the reasoning behind each step."
        )

        # Step 3: Ensembling multiple solutions (e.g., from different reasoning paths or iterations)
        solutions = [reasoning_solution, initial_answer]
        ensemble_result = await self.sc_ensemble(solutions=solutions)

        # Step 4: Review the ensemble result to improve clarity, accuracy, or completeness
        final_review = await self.review(pre_solution=ensemble_result)

        return final_review