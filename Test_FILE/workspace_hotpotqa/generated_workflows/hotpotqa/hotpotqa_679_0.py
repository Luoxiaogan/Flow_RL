# Workflow ID: hotpotqa_679_0
# Benchmark: hotpotqa
# Data Indices: [2784, 3137, 2027, 860]

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
        # Step 1: Use FlexibleCustom with sequential multi-hop pattern to trace connections step-by-step
        solution_step_by_step = await self.flexible_custom(
            custom_instruction="Break down the problem into smaller steps and explain the reasoning behind each step.",
            reasoning_pattern="sequential",
            steps=["identify_key_entities", "find_intermediate_connections", "trace_reasoning_path", "synthesize_final_answer"]
        )

        # Step 2: Generate a direct answer as a baseline
        direct_answer = await self.answer_generate()

        # Step 3: Ensemble both solutions to improve accuracy
        ensemble_solution = await self.sc_ensemble(solutions=[solution_step_by_step, direct_answer])

        # Step 4: Review the ensemble result for refinement
        final_solution = await self.review(pre_solution=ensemble_solution)

        return final_solution