# Workflow ID: gsm8k_381_1
# Benchmark: gsm8k
# Data Indices: [393, 486]

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
        This is a diverse and efficient workflow using the Reflect and Regenerate pattern with parallel exploration.
        It first generates multiple initial solutions in parallel (fan-out), then selects the best one via ensemble,
        and finally applies a reflective critique to guide a targeted re-solution — all while maintaining logical flow
        and leveraging the new Reflect operator for meta-cognitive improvement.
        """
        # Step 1: Generate three independent solutions using parallel reasoning (fan-out)
        solution1 = await self.flexible_custom(
            reasoning_pattern="parallel",
            steps=["analyze", "plan", "solve"],
            custom_instruction="Approach the problem from a different angle each time."
        )
        
        solution2 = await self.flexible_custom(
            reasoning_pattern="parallel",
            steps=["identify_knowns", "apply_logic", "verify"],
            custom_instruction="Break down the problem into known facts and derive conclusions step-by-step."
        )

        solution3 = await self.flexible_custom(
            reasoning_pattern="parallel",
            steps=["define_variables", "formulate_equations", "compute"],
            custom_instruction="Model the problem mathematically and solve systematically."
        )

        # Step 2: Use ScEnsemble to select the best-performing initial solution
        solutions = [solution1, solution2, solution3]
        best_initial = await self.sc_ensemble(solutions=solutions)

        # Step 3: Critically reflect on the best initial solution to uncover hidden assumptions or gaps
        reflection = await self.reflect(pre_solution=best_initial)

        # Step 4: Use the reflection to generate a final, improved solution that addresses the identified issues
        final_solution = await self.custom(
            instruction=f"Given the following reflection: '{reflection}'. Now, solve the problem again with enhanced clarity, precision, and logical rigor."
        )

        return final_solution