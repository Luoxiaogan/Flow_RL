# Workflow ID: gsm8k_163_1
# Benchmark: gsm8k
# Data Indices: [770, 920]

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
        Reflect and Regenerate Workflow: 
        Generate an initial solution, critically reflect on it, then use that reflection to guide a new, improved solution.
        This mimics human meta-cognition — evaluating one's own reasoning before refining it.
        """
        # Step 1: Generate an initial solution using flexible custom with sequential reasoning
        initial_solution = await self.flexible_custom(
            custom_instruction="Solve the problem by breaking it into logical steps.",
            reasoning_pattern="sequential",
            steps=["identify_knowns", "define_unknowns", "apply_logic", "compute_answer"]
        )

        # Step 2: Critically reflect on the initial solution — identify assumptions, gaps, or alternative interpretations
        reflection = await self.reflect(pre_solution=initial_solution)

        # Step 3: Use the reflection to craft a targeted instruction for a refined solution
        refined_instruction = f"Given the following reflection on the initial approach: '{reflection}'. Now, solve the problem again with deeper analysis and corrected logic."
        
        # Step 4: Generate a final solution based on the reflection — this is where insight and improvement happen
        final_answer = await self.custom(instruction=refined_instruction)

        return final_answer