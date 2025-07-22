# Workflow ID: hotpotqa_188_0
# Benchmark: hotpotqa
# Data Indices: [558, 723, 788, 2299]

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
        It first generates an initial answer, then refines it through iterative steps.
        Finally, it ensembles multiple solutions to produce the best result.
        """
        # Step 1: Generate an initial answer using direct reasoning
        initial_answer = await self.answer_generate()

        # Step 2: Use flexible custom with sequential reasoning to trace multi-hop connections
        multi_hop_solution = await self.flexible_custom(
            custom_instruction="Break down the problem step-by-step and trace connections between different pieces of information.",
            reasoning_pattern="sequential",
            steps=["identify_key_entities", "find_intermediate_connections", "trace_reasoning_path", "synthesize_final_answer"]
        )

        # Step 3: Review the initial answer to improve it
        reviewed_answer = await self.review(pre_solution=initial_answer)

        # Step 4: Create a list of candidate solutions for ensemble
        solutions = [
            initial_answer,
            reviewed_answer,
            multi_hop_solution
        ]

        # Step 5: Ensemble the solutions to select the best one
        final_answer = await self.sc_ensemble(solutions=solutions)

        return final_answer