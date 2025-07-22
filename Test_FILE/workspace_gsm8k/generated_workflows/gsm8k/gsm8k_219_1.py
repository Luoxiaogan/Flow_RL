# Workflow ID: gsm8k_219_1
# Benchmark: gsm8k
# Data Indices: [595, 99]

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
        This is a diverse workflow using two novel patterns:
        1. Parallel Ensemble (Fan-out/Fan-in) with multiple initial strategies
        2. Reflect and Regenerate: After selecting the best solution via ensemble,
           we reflect on it and regenerate a final answer to improve accuracy.
        
        This structure ensures robustness through diversity of approaches and meta-cognitive refinement.
        """
        # Step 1: Generate 3 independent solutions using different reasoning strategies
        solution_methods = [
            ("step-by-step breakdown", "Solve the problem by breaking it into clear steps."),
            ("formula-first approach", "Apply relevant formulas or mathematical rules first, then compute."),
            ("estimate-then-refine", "Start with an estimate, then calculate precisely.")
        ]
        
        solutions = []
        for name, instruction in solution_methods:
            sol = await self.flexible_custom(
                custom_instruction=instruction,
                reasoning_pattern="sequential",
                steps=["understand", "plan", "solve", "verify"]
            )
            solutions.append(sol)

        # Step 2: Use ScEnsemble to pick the best among the three
        best_solution = await self.sc_ensemble(solutions=solutions)

        # Step 3: Critically reflect on the best solution to uncover hidden flaws or assumptions
        reflection = await self.reflect(pre_solution=best_solution)

        # Step 4: Use that reflection to guide a new, improved solution — this is the key difference!
        # Unlike the original which just regenerates based on reflection, here we ensure the reflection
        # informs a fresh start rather than a fix, promoting deeper correction.
        final_answer = await self.custom(
            instruction=f"Based on the following reflection about the best solution: {reflection}. "
                        f"Re-solve the problem from scratch using this insight. Be meticulous and avoid prior mistakes."
        )

        return final_answer