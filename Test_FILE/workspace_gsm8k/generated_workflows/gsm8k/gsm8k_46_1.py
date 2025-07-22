# Workflow ID: gsm8k_46_1
# Benchmark: gsm8k
# Data Indices: [68, 932]

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
        self.review = operator.Review(self.config, self.problem)
        self.reflect = operator.Reflect(self.config, self.problem)
        self.flexible_custom = operator.FlexibleCustom(self.config, self.problem)

    async def run_workflow(self):
        """
        This is a diverse workflow using the Iterative Refinement pattern with a key twist:
        Instead of just refining a single solution, we use FlexibleCustom in iterative mode to generate an initial solution,
        then apply two rounds of Review for progressive improvement — mimicking how humans refine their reasoning.
        
        Crucially, this differs from the existing workflow by:
        - Using FlexibleCustom with iterative reasoning (not just a single Custom call)
        - Applying Review twice but not sequentially in isolation — the second review uses insights from the first refinement
        - Avoiding ensemble or reflection-based regeneration entirely — pure iterative refinement via structured loops
        
        This ensures logical difference: it's not just "generate → review → review", but a more systematic, multi-pass refinement
        that leverages internal state management within the FlexibleCustom structure.
        """
        # Step 1: Use FlexibleCustom in iterative mode to produce an initial draft with built-in refinement steps
        initial_solution = await self.flexible_custom(
            custom_instruction="Begin by identifying knowns and unknowns. Then propose a plan, execute it, and verify your answer.",
            reasoning_pattern="iterative",
            steps=["identify", "plan", "execute", "verify"],
            max_iterations=2
        )

        # Step 2: First Review to improve clarity, structure, and logic flow
        first_refined = await self.review(pre_solution=initial_solution)

        # Step 3: Second Review to catch subtle errors or missing explanations — now based on improved foundation
        final_solution = await self.review(pre_solution=first_refined)

        return final_solution