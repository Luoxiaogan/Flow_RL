# Workflow ID: gsm8k_357_1
# Benchmark: gsm8k
# Data Indices: [622, 533]

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
        This is a diverse and complex workflow using the Iterative Refinement pattern.
        Step 1: Generate an initial solution with a clear, structured prompt.
        Step 2: Apply Review at least twice to progressively refine the solution.
        Step 3: Use Reflect after the second review to identify subtle flaws or assumptions that may have been missed.
        Step 4: Finalize by generating a polished answer based on both the iterative improvements and reflective critique.
        
        This logic differs from the existing one by focusing on progressive refinement through repeated review (not parallel ensembling), 
        and it uses reflection not just as a post-hoc check but as a meta-cognitive input to guide final polishing — ensuring depth over breadth.
        """
        # --- INITIAL SOLUTION ---
        initial_solution = await self.custom(
            instruction="Solve the problem step-by-step, showing all calculations clearly. Break down each part of the problem logically."
        )

        # --- ITERATIVE REFINEMENT (at least two reviews) ---
        current_solution = initial_solution
        for iteration in range(2):  # Exactly two iterations of refinement
            current_solution = await self.review(pre_solution=current_solution)

        # --- REFLECTION FOR DEEPER INSIGHT ---
        reflection = await self.reflect(pre_solution=current_solution)

        # --- FINAL POLISHING BASED ON REFLECTION ---
        final_instruction = (
            f"Given the following reflection:\n{reflection}\n\n"
            "Revise your solution again to address any overlooked issues, clarify reasoning, and ensure mathematical correctness."
        )
        final_answer = await self.custom(instruction=final_instruction)

        return final_answer