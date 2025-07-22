# Workflow ID: gsm8k_390_1
# Benchmark: gsm8k
# Data Indices: [691, 510]

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
        Iterative Refinement Pattern (Fundamentally Different Logic):
        1. Generate an initial solution using a flexible custom operator with a sequential reasoning pattern.
        2. Apply the Review operator twice to progressively refine the solution — each time improving clarity, logic, or completeness.
        3. This creates a meta-loop of self-improvement without branching, ensembling, or reflection-based regeneration.
        4. The simplicity and repetition ensure robustness through refinement rather than diversity of approaches.

        Why this is different:
        - No parallel processing or ensemble selection (unlike existing).
        - No reflection-to-regeneration loop (unlike existing).
        - Uses only one path, but iteratively improves it via structured review steps.
        - Demonstrates that iterative improvement can be more effective than multi-path exploration in some cases.
        """

        # --- STEP 1: Initial Solution via FlexibleCustom (Sequential Reasoning) ---
        initial_solution = await self.flexible_custom(
            custom_instruction="Solve the problem by following a clear sequence: analyze the question, identify knowns and unknowns, apply relevant principles, and compute the answer.",
            reasoning_pattern="sequential",
            steps=["analyze", "identify", "apply", "compute"]
        )

        # --- STEP 2: First Review (Improve Clarity and Structure) ---
        refined_solution_1 = await self.review(pre_solution=initial_solution)

        # --- STEP 3: Second Review (Enhance Logical Rigor and Completeness) ---
        refined_solution_2 = await self.review(pre_solution=refined_solution_1)

        return refined_solution_2