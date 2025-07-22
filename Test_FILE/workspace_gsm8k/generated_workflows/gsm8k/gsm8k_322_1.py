# Workflow ID: gsm8k_322_1
# Benchmark: gsm8k
# Data Indices: [251, 792]

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
        Diverse and efficient workflow using Parallel Ensemble + Reflect + Iterative Refinement.
        This pattern first generates multiple independent solutions (parallel), selects the best one,
        then reflects on it to identify blind spots, and finally refines the solution iteratively.
        It combines fan-out/fan-in with meta-cognitive reflection and progressive improvement — 
        fundamentally different from the existing single-path approach.
        """

        # Step 1: Generate multiple candidate solutions in parallel (fan-out)
        solution_candidates = []
        for i in range(3):  # Three different reasoning strategies
            instruction = (
                "Solve this math problem by focusing on a unique strategy: "
                f"Approach {i+1}: Use estimation first, then precise calculation."
                if i == 0 else
                "Approach 2: Break the problem into sub-problems and solve each separately."
                if i == 1 else
                "Approach 3: Assume a simpler version of the problem and scale up."
            )
            candidate = await self.custom(instruction=instruction)
            solution_candidates.append(candidate)

        # Step 2: Select the best solution via ensemble (fan-in)
        best_candidate = await self.sc_ensemble(solutions=solution_candidates)

        # Step 3: Critically reflect on the best solution without rewriting it
        reflection = await self.reflect(pre_solution=best_candidate)

        # Step 4: Use iterative FlexibleCustom to refine based on reflection
        refined_solution = await self.flexible_custom(
            custom_instruction=f"Refine the following solution using this reflection: {reflection}. "
                               "Follow a structured iterative process: analyze assumptions, improve logic, verify results.",
            previous_results=[best_candidate],
            reasoning_pattern="iterative",
            steps=["analyze_assumptions", "improve_logic", "verify_result"],
            max_iterations=2
        )

        return refined_solution