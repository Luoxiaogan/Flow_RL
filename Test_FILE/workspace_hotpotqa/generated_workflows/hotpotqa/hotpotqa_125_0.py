# Workflow ID: hotpotqa_125_0
# Benchmark: hotpotqa
# Data Indices: [1395, 3623, 3960, 2037, 2937]

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
        It first generates an initial answer, then uses flexible custom to trace multi-hop connections,
        and finally reviews the solution for refinement.
        """
        # Step 1: Generate an initial answer directly
        initial_answer = await self.answer_generate()

        # Step 2: Use FlexibleCustom with sequential reasoning to trace multi-hop connections
        multi_hop_solution = await self.flexible_custom(
            custom_instruction="Break down the problem into smaller steps, identify key entities, and trace logical connections between them step-by-step.",
            reasoning_pattern="sequential",
            steps=["identify_entities", "find_connections", "trace_reasoning_path", "synthesize_answer"]
        )

        # Step 3: Ensemble both solutions to improve robustness
        ensemble_solution = await self.sc_ensemble(solutions=[initial_answer, multi_hop_solution])

        # Step 4: Review the ensemble solution to refine it
        final_solution = await self.review(pre_solution=ensemble_solution)

        return final_solution