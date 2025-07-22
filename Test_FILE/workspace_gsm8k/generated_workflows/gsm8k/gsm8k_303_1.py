# Workflow ID: gsm8k_303_1
# Benchmark: gsm8k
# Data Indices: [576, 193, 342]

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
        Parallel Ensemble + Final Review Workflow:
        1. Generate 3 diverse solutions using different reasoning strategies via FlexibleCustom.
        2. Use ScEnsemble to select the most consistent and accurate solution.
        3. Apply a final review to polish clarity and correctness — ensuring robustness through diversity and consensus.
        
        This approach leverages multiple perspectives (parallel) and reduces reliance on any single flawed reasoning path.
        """
        # Step 1: Generate 3 distinct solutions using varied reasoning patterns
        solutions = []
        for i in range(3):
            if i == 0:
                # Sequential reasoning: step-by-step breakdown
                solution = await self.flexible_custom(
                    custom_instruction="Use a structured, sequential approach: identify knowns, unknowns, apply formulas, verify.",
                    reasoning_pattern="sequential",
                    steps=["identify_knowns", "identify_unknowns", "apply_formula", "verify"]
                )
            elif i == 1:
                # Iterative refinement: start with estimation, then refine
                solution = await self.flexible_custom(
                    custom_instruction="Begin with an estimate, then improve iteratively over 2 passes.",
                    reasoning_pattern="iterative",
                    steps=["initial_estimate", "refine", "finalize"],
                    max_iterations=2
                )
            else:
                # Branching logic: consider alternative interpretations first
                solution = await self.flexible_custom(
                    custom_instruction="First explore possible interpretations or edge cases, then solve based on the most plausible one.",
                    reasoning_pattern="branching",
                    steps=["analyze_possibilities", "choose_best_path", "solve"]
                )
            solutions.append(solution)

        # Step 2: Use ensemble to pick the best solution based on consistency and accuracy
        best_solution = await self.sc_ensemble(solutions=solutions)

        # Step 3: Final review to enhance clarity, fix subtle issues, and ensure completeness
        final_answer = await self.review(pre_solution=best_solution)

        return final_answer