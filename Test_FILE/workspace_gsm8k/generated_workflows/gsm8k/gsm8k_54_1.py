# Workflow ID: gsm8k_54_1
# Benchmark: gsm8k
# Data Indices: [789, 646, 521]

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
        It introduces a novel structure: first generate an initial solution, then critically reflect on it
        without rewriting it, and finally use that reflection to guide a targeted, improved solution.
        This mimics human meta-cognition — evaluating one's own reasoning before refining it.
        Unlike the existing workflow, this uses no iterative refinement or ensemble methods;
        instead, it focuses on deep introspection as a catalyst for improvement.
        """
        # Step 1: Generate an initial solution using a general-purpose reasoning prompt
        initial_solution = await self.custom(
            instruction="Solve the problem step-by-step, showing all calculations clearly."
        )

        # Step 2: Critically reflect on the solution — identify assumptions, gaps, or potential errors
        reflection = await self.reflect(pre_solution=initial_solution)

        # Step 3: Use the reflection to craft a new, focused custom instruction that addresses weaknesses
        refined_instruction = (
            f"Given the following reflection on your earlier attempt: '{reflection}'. "
            "Now, solve the problem again with greater attention to precision, clarity, and logical completeness. "
            "Avoid repeating the same mistakes identified in the reflection."
        )

        # Step 4: Generate a final, improved solution based on the reflection
        final_solution = await self.custom(instruction=refined_instruction)

        return final_solution