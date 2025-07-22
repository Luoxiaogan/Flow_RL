# Workflow ID: hotpotqa_380_0
# Benchmark: hotpotqa
# Data Indices: [1757, 3441, 2822, 1909, 2116]

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
        This is a robust workflow graph for multi-hop question answering.
        It uses multiple reasoning paths and ensemble to improve accuracy.
        """
        # Step 1: Generate initial answer using direct reasoning
        direct_answer = await self.answer_generate()

        # Step 2: Generate alternative reasoning paths via Custom with step-by-step instructions
        step_by_step_1 = await self.custom(instruction="Break down the problem into smaller steps and explain each reasoning step clearly.")
        step_by_step_2 = await self.custom(instruction="Solve this by identifying key entities and tracing connections between them.")

        # Step 3: Use FlexibleCustom for structured multi-hop reasoning (sequential pattern)
        multi_hop_reasoning = await self.flexible_custom(
            custom_instruction="Use sequential reasoning to trace connections across information sources.",
            reasoning_pattern="sequential",
            steps=["identify_key_entities", "find_intermediate_connections", "trace_path_to_answer", "synthesize_final_answer"]
        )

        # Step 4: Ensemble all solutions to select the best one
        solutions = [direct_answer, step_by_step_1, step_by_step_2, multi_hop_reasoning]
        ensembled_solution = await self.sc_ensemble(solutions=solutions)

        # Step 5: Final review to verify and refine the ensemble result
        final_answer = await self.review(pre_solution=ensembled_solution)

        return final_answer