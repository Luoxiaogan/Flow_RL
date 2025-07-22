# Workflow ID: hotpotqa_4_0
# Benchmark: hotpotqa
# Data Indices: [291, 2582, 1975, 3883]

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
        It first breaks down the problem step-by-step, then refines and ensembles solutions.
        """
        # Step 1: Use FlexibleCustom with sequential reasoning to trace multi-hop connections
        solution_1 = await self.flexible_custom(
            custom_instruction="Break down the problem into smaller steps and explain each reasoning step clearly.",
            reasoning_pattern="sequential",
            steps=["identify_key_entities", "find_intermediate_connections", "trace_reasoning_path", "synthesize_final_answer"]
        )

        # Step 2: Generate an answer directly as a baseline
        solution_2 = await self.answer_generate()

        # Step 3: Review the initial flexible custom solution for refinement
        refined_solution_1 = await self.review(pre_solution=solution_1)

        # Step 4: Ensemble the two solutions (flexible custom + direct answer)
        ensemble_solution = await self.sc_ensemble(solutions=[refined_solution_1, solution_2])

        return ensemble_solution