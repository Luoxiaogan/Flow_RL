# Workflow ID: hotpotqa_99_0
# Benchmark: hotpotqa
# Data Indices: [220, 108, 1010, 3149, 3501]

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
        It uses multiple reasoning paths to enhance robustness and ensembles the best solution.
        """
        # Step 1: Generate initial answer directly
        direct_answer = await self.answer_generate()

        # Step 2: Use flexible custom with sequential reasoning to break down the problem
        seq_reasoning = await self.flexible_custom(
            custom_instruction="Break down the problem step-by-step and explain each reasoning step in detail.",
            reasoning_pattern="sequential",
            steps=["identify_key_entities", "find_intermediate_connections", "trace_logical_path", "synthesize_final_answer"]
        )

        # Step 3: Use Custom with detailed reasoning instruction to generate an alternative path
        detailed_reasoning = await self.custom(
            instruction="Solve this by breaking it into smaller logical steps and explaining your reasoning at each step."
        )

        # Step 4: Ensemble all generated solutions to select the most consistent one
        solutions = [direct_answer, seq_reasoning, detailed_reasoning]
        ensembled_solution = await self.sc_ensemble(solutions=solutions)

        # Step 5: Final review to refine and verify the selected solution
        final_answer = await self.review(pre_solution=ensembled_solution)

        return final_answer