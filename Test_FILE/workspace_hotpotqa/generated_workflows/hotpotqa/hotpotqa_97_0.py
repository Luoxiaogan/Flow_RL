# Workflow ID: hotpotqa_97_0
# Benchmark: hotpotqa
# Data Indices: [18, 339, 2338, 2667]

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
        This is a workflow graph for multi-hop question answering using iterative refinement.
        Starts with an initial answer, then iteratively refines it through review and custom reasoning.
        """
        # Step 1: Generate an initial answer (directly from the problem)
        initial_answer = await self.answer_generate()
        
        # Step 2: Use flexible_custom to perform iterative refinement
        # Reasoning pattern: iterative with structured output for step-by-step verification
        refined_answer = await self.flexible_custom(
            custom_instruction="Start with an initial answer, then verify each claim against the context step by step. If any claim is unsupported or contradicted, revise accordingly.",
            reasoning_pattern="iterative",
            steps=["initial_hypothesis", "verify_facts", "refine_answer"],
            max_iterations=3,
            use_structured_output=True
        )

        # Step 3: Optionally, ensemble multiple solutions if needed
        # For now, we only have one refined solution; this can be extended if more solutions are generated
        return refined_answer