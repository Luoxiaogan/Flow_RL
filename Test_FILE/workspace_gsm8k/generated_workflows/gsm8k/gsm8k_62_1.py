# Workflow ID: gsm8k_62_1
# Benchmark: gsm8k
# Data Indices: [992, 418, 540]

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
        This is a diverse and robust workflow using the Iterative Refinement pattern.
        Starts with an initial solution, then applies Review twice to progressively improve it.
        This mimics human-like learning: generate → critique → refine → critique again → finalize.
        The logic is fundamentally different from the existing ensemble-based approach:
        - No parallel solutions or ensembling
        - No reflection-driven regeneration
        - Uses only sequential refinement via Review
        - Focuses on depth over breadth of reasoning
        """

        # Step 1: Generate an initial solution using a structured but flexible approach
        initial_solution = await self.flexible_custom(
            custom_instruction="Break down the problem into clear steps: identify what is given, what needs to be calculated, and how they relate.",
            reasoning_pattern="sequential",
            steps=["identify_input", "define_operation", "compute_result", "present_answer"]
        )

        # Step 2: First review — focus on logical consistency and completeness
        first_refined = await self.review(pre_solution=initial_solution)

        # Step 3: Second review — focus on clarity, precision, and potential errors in calculation
        second_refined = await self.review(pre_solution=first_refined)

        # Step 4: Final output — no ensemble needed; just return the best refined version
        final_answer = second_refined

        return final_answer