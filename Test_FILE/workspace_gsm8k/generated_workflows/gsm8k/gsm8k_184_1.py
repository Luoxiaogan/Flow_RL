# Workflow ID: gsm8k_184_1
# Benchmark: gsm8k
# Data Indices: [725, 564, 291]

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
        This is a diverse and effective workflow using two distinct patterns:
        1. Parallel Ensemble (Fan-out): Generate multiple initial solutions with different reasoning styles.
        2. Reflect-and-Regenerate: Use reflection on the best solution to guide a final refinement.

        The logic is fundamentally different from the existing workflow:
        - It starts with parallel exploration instead of sequential generation.
        - It uses ensemble selection before any reflection or review — not after.
        - It combines both "Parallel Ensemble" and "Reflect and Regenerate" patterns in a novel sequence.
        """
        # Step 1: Generate 3 independent solutions using different reasoning strategies via FlexibleCustom
        # Each uses a unique pattern to encourage diverse approaches
        solutions = []
        for i in range(3):
            pattern_map = {
                0: "sequential",
                1: "iterative",
                2: "branching"
            }
            step_config = {
                0: ["understand", "analyze", "solve", "verify"],
                1: ["initial_guess", "refine", "final_check"],
                2: ["identify_assumptions", "evaluate_options", "choose_best"]
            }

            solution = await self.flexible_custom(
                custom_instruction="Solve the problem with clear reasoning steps.",
                reasoning_pattern=pattern_map[i],
                steps=step_config[i],
                use_structured_output=True
            )
            solutions.append(solution)

        # Step 2: Use ScEnsemble to select the best solution among the three
        best_solution = await self.sc_ensemble(solutions=solutions)

        # Step 3: Critically reflect on the selected solution to uncover hidden flaws or assumptions
        reflection = await self.reflect(pre_solution=best_solution)

        # Step 4: Use that reflection to generate a new, improved final answer
        final_answer = await self.custom(
            instruction=f"Based on this reflection: '{reflection}', re-solve the problem carefully. "
                        f"Ensure your final answer addresses any potential weaknesses identified above."
        )

        return final_answer