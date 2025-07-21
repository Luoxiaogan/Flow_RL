# Workflow ID: gsm8k_63_1
# Benchmark: gsm8k
# Data Indices: [531, 111]

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
        This workflow combines two distinct patterns:
        1. Iterative Refinement (for robustness in reasoning)
        2. Reflect and Regenerate (to leverage meta-cognition for improvement)

        It starts with a parallel ensemble to generate diverse initial solutions,
        then uses iterative refinement on the best one, guided by reflection at each step.
        This hybrid approach ensures both breadth (from ensembling) and depth (from reflection).
        """

        # --- STEP 1: Generate multiple candidate solutions via Parallel Ensemble ---
        solution_list = []
        instructions = [
            "Solve the problem using clear, logical steps.",
            "Break the problem into sub-problems and solve each independently.",
            "Apply the order of operations strictly and verify intermediate results."
        ]
        
        for instruction in instructions:
            solution = await self.custom(instruction=instruction)
            solution_list.append(solution)

        # --- STEP 2: Select the best solution using ScEnsemble ---
        best_solution = await self.sc_ensemble(solutions=solution_list)

        # --- STEP 3: Apply Iterative Refinement with Reflection ---
        current_solution = best_solution
        max_iterations = 3
        for i in range(max_iterations):
            # Reflect on the current solution to identify potential flaws or improvements
            reflection = await self.reflect(pre_solution=current_solution)
            
            # Use the reflection to guide a new Custom call that incorporates insights
            improved_instruction = (
                f"Given the following reflection on the previous attempt: {reflection}. "
                "Revise your solution accordingly, focusing on clarity, accuracy, and completeness."
            )
            current_solution = await self.custom(instruction=improved_instruction)
            
            # Optional: Add early termination if reflection indicates no significant change
            if i < max_iterations - 1:
                # We continue refining; this is the core of the iterative loop
                pass

        # --- STEP 4: Final Review for polish and correctness ---
        final_answer = await self.review(pre_solution=current_solution)

        return final_answer