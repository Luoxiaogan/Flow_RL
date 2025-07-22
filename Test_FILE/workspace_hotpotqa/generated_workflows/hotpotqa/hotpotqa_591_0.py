# Workflow ID: hotpotqa_591_0
# Benchmark: hotpotqa
# Data Indices: [1317, 2178, 1944, 2057]

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
        It breaks down the problem into steps and traces connections across context sources.
        """
        # Step 1: Use FlexibleCustom with sequential reasoning to trace multi-hop connections
        sequential_solution = await self.flexible_custom(
            custom_instruction="Break down the problem step-by-step and trace logical connections between entities in the context.",
            reasoning_pattern="sequential",
            steps=["identify_key_entities", "find_intermediate_connections", "trace_reasoning_path", "synthesize_final_answer"]
        )

        # Step 2: Generate an independent direct answer for comparison
        direct_answer = await self.answer_generate()

        # Step 3: Ensemble both solutions to improve robustness
        ensemble_result = await self.sc_ensemble(solutions=[sequential_solution, direct_answer])

        # Step 4: Review the ensembled solution for refinement
        final_solution = await self.review(pre_solution=ensemble_result)

        return final_solution