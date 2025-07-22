# Workflow ID: gsm8k_57_1
# Benchmark: gsm8k
# Data Indices: [100, 226]

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
        This is a diverse and complex workflow that emphasizes the 'Reflect and Regenerate' pattern as its core logic.
        
        Key differences from existing workflow:
        - Starts with a single solution (not parallel ensemble), then reflects deeply before regenerating.
        - Uses FlexibleCustom in a branching pattern to explore multiple reasoning paths based on reflection.
        - No ScEnsemble — instead of selecting from multiple solutions, it uses reflection to guide one superior path.
        - Leverages structured reasoning steps in FlexibleCustom for deeper logical exploration after reflection.
        """

        # Step 1: Generate an initial solution using a basic custom prompt
        initial_solution = await self.custom(
            instruction="Solve the problem step-by-step, explaining your reasoning clearly."
        )

        # Step 2: Critically reflect on the solution — identify assumptions, gaps, or errors
        reflection = await self.reflect(pre_solution=initial_solution)

        # Step 3: Use the reflection to drive a new, targeted solution via FlexibleCustom in branching mode
        # This allows us to explore different reasoning strategies based on the critique
        flexible_branching = operator.FlexibleCustom(
            self.config,
            self.problem,
            reasoning_pattern="branching",
            steps=["reconstruct", "validate_assumptions", "correct_errors"],
            use_structured_output=True
        )

        # Construct a dynamic instruction that tells the model how to proceed based on reflection
        instruction_for_branching = (
            "Based on the following reflection about the initial solution, "
            "reconstruct the answer by addressing each point raised. "
            "Use a branching approach: first reconstruct the logic, then validate all assumptions, "
            "and finally correct any identified errors. Be precise and systematic. "
            f"Reflection: {reflection}"
        )

        # Step 4: Run the branching FlexibleCustom to generate a refined solution
        refined_solution = await flexible_branching(
            custom_instruction=instruction_for_branching
        )

        # Step 5: Optional iterative review — apply Review to further polish the final output
        final_solution = await self.review(pre_solution=refined_solution)

        return final_solution