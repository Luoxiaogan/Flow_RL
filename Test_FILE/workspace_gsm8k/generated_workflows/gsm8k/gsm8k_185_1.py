# Workflow ID: gsm8k_185_1
# Benchmark: gsm8k
# Data Indices: [21, 493]

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
        This is a diverse and efficient workflow using the 'Reflect and Regenerate' pattern.
        It generates an initial solution, critically reflects on it to uncover potential flaws or improvements,
        then uses that reflection to guide a new, more robust solution — mimicking human metacognition.
        This approach ensures deep reasoning over surface-level correctness.
        """
        # Step 1: Generate an initial solution using FlexibleCustom in sequential mode for structured thinking
        initial_solution = await self.flexible_custom(
            reasoning_pattern="sequential",
            steps=["analyze_problem", "identify_components", "formulate_equations", "compute_answer"],
            custom_instruction="Solve this math word problem by breaking it into clear logical steps."
        )

        # Step 2: Critically reflect on the initial solution — do not rewrite yet
        reflection_text = await self.reflect(pre_solution=initial_solution)

        # Step 3: Use the reflection to guide a fresh, targeted Custom call for improved accuracy
        final_solution = await self.custom(
            instruction=f"Given the following reflection on the initial attempt: '{reflection_text}'. "
                        f"Re-solve the problem with greater precision, focusing on any identified weaknesses or overlooked aspects."
        )

        return final_solution