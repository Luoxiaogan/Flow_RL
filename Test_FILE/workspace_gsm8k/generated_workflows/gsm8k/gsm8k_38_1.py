# Workflow ID: gsm8k_38_1
# Benchmark: gsm8k
# Data Indices: [121, 618, 498]

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
        This is a diverse and effective workflow using the 'Iterative Refinement' pattern with a twist:
        - First, generate an initial solution via FlexibleCustom (sequential reasoning).
        - Then, use Reflect to critique it deeply.
        - Finally, apply iterative refinement: repeatedly review the solution while incorporating reflection insights until convergence or max iterations.
        
        This approach combines meta-cognition (reflection) with structured iteration — mimicking how humans improve solutions through cycles of feedback.
        """
        # Step 1: Generate an initial solution using structured, step-by-step reasoning
        initial_solution = await self.flexible_custom(
            custom_instruction="Solve the problem by breaking it into clear steps: understand, analyze, compute, verify.",
            reasoning_pattern="sequential",
            steps=["understand", "analyze", "compute", "verify"]
        )

        # Step 2: Critically reflect on the initial solution to uncover hidden assumptions, logic gaps, or clarity issues
        reflection = await self.reflect(pre_solution=initial_solution)

        # Step 3: Iteratively refine the solution using Review, guided by the reflection
        current_solution = initial_solution
        for i in range(2):  # Perform up to 2 refinement cycles
            # Use the reflection as context to guide improvement
            refined_instruction = (
                f"Based on this reflection: '{reflection}'. "
                f"Improve the following solution by addressing any flaws, enhancing clarity, and ensuring accuracy:\n\n{current_solution}"
            )
            current_solution = await self.review(pre_solution=current_solution)
            
            # Optional: Re-reflect after each review to check if further improvements are needed
            new_reflection = await self.reflect(pre_solution=current_solution)
            if "no major flaws" in new_reflection.lower() or i == 1:
                break

        return current_solution