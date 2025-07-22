# Workflow ID: hotpotqa_308_0
# Benchmark: hotpotqa
# Data Indices: [3381, 988, 3422, 1963]

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
        It uses sequential reasoning to extract and connect facts, then synthesizes the answer with custom instruction,
        and finally reviews the solution for validation.
        """
        # Step 1: Use FlexibleCustom with sequential reasoning to break down and connect information
        flexible_solution = await self.flexible_custom(
            custom_instruction="Break down the problem into smaller steps and trace connections between pieces of evidence.",
            reasoning_pattern="sequential",
            steps=["identify_key_entities", "extract_facts", "find_intermediate_connections", "synthesize_answer"]
        )

        # Step 2: Use Custom to synthesize a clear, step-by-step explanation based on the flexible solution
        synthesized_solution = await self.custom(
            instruction="Explain how to solve this problem by breaking it down into detailed steps and explaining the reasoning behind each step."
        )

        # Step 3: Generate an initial answer using AnswerGenerate as a baseline
        baseline_answer = await self.answer_generate()

        # Step 4: Ensemble multiple solutions (flexible + custom + baseline) to improve robustness
        ensemble_solutions = [flexible_solution, synthesized_solution, baseline_answer]
        ensembled_answer = await self.sc_ensemble(solutions=ensemble_solutions)

        # Step 5: Review the ensembled solution to refine and validate
        final_answer = await self.review(pre_solution=ensembled_answer)

        return final_answer