# Workflow ID: gsm8k_16_1
# Benchmark: gsm8k
# Data Indices: [194, 553, 435]

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
        This is a diverse and effective workflow using the 'Parallel Ensemble + Reflect and Regenerate' hybrid pattern.
        It first generates multiple independent solutions (parallel), then uses reflection to refine one of them into a superior final answer.
        This approach combines robustness (from ensemble) with meta-cognition (from reflection).
        """

        # Step 1: Generate 3 independent solutions using different reasoning styles via FlexibleCustom
        solution_a = await self.flexible_custom(
            custom_instruction="Solve step-by-step by identifying all time components first, then summing them.",
            reasoning_pattern="sequential",
            steps=["identify_time_components", "convert_to_common_unit", "sum_total_time"]
        )

        solution_b = await self.flexible_custom(
            custom_instruction="Start with the total pages written and work backward to find total time spent.",
            reasoning_pattern="iterative",
            steps=["start_from_output", "reverse_engineer_input", "validate_with_knowns"],
            max_iterations=2
        )

        solution_c = await self.flexible_custom(
            custom_instruction="Break the problem into three phases: research, writing, editing — solve each separately.",
            reasoning_pattern="branching",
            steps=["research_phase", "writing_phase", "editing_phase", "combine_results"]
        )

        # Step 2: Use ScEnsemble to select the best among the three initial solutions
        candidate_solutions = [solution_a, solution_b, solution_c]
        best_solution = await self.sc_ensemble(solutions=candidate_solutions)

        # Step 3: Critically reflect on the selected best solution to uncover hidden assumptions or errors
        reflection = await self.reflect(pre_solution=best_solution)

        # Step 4: Generate a final refined solution based on both the original best solution and the reflection
        final_solution = await self.custom(
            instruction=f"Given this initial solution:\n{best_solution}\n\nAnd this critical reflection:\n{reflection}\n\nNow produce a fully revised and accurate answer."
        )

        return final_solution