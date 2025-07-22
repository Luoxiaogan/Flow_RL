# Workflow ID: gsm8k_187_1
# Benchmark: gsm8k
# Data Indices: [195, 502]

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
        1. Generate an initial solution using a flexible custom approach with sequential reasoning.
        2. Critically reflect on the solution to uncover hidden assumptions or gaps.
        3. Use that reflection as a guide to generate a superior, more accurate final answer.
        
        This pattern mimics human metacognition — not just solving, but thinking about how we solve.
        It avoids blind refinement (like iterative review) and instead uses insight from critique to reframe the problem.
        """
        # Step 1: Generate an initial solution using structured, step-by-step reasoning
        initial_solution = await self.flexible_custom(
            custom_instruction="Solve this problem by first identifying all known quantities, then determining what needs to be calculated, and finally performing the necessary operations in a logical sequence.",
            reasoning_pattern="sequential",
            steps=["identify_knowns", "define_unknowns", "formulate_plan", "execute_calculation"]
        )

        # Step 2: Reflect critically on the initial solution — do NOT rewrite it yet
        reflection_text = await self.reflect(pre_solution=initial_solution)

        # Step 3: Use the reflection to guide a new, improved solution
        final_answer = await self.custom(
            instruction=f"Given the initial solution below and the following reflection on potential weaknesses or oversights: {reflection_text}. Now, provide a revised solution that addresses these points while maintaining clarity and correctness."
        )

        return final_answer