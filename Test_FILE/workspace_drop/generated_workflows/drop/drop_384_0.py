# Workflow ID: drop_384_0
# Benchmark: drop
# Data Indices: [3442, 1703, 2806, 3059]

class Workflow:
    def __init__(
        self,
        config,
        problem
    ) -> None:
        self.problem = problem
        self.problem_text = str(problem) if isinstance(problem, dict) else problem
        self.config = create(config)
        self.custom = operator.Custom(self.config, self.problem)
        self.sc_ensemble = operator.ScEnsemble(self.config, self.problem)
        self.answer_generate = operator.AnswerGenerate(self.config, self.problem)
        self.review = operator.Review(self.config, self.problem)
        self.counting_reasoning = operator.CountingReasoning(self.config, self.problem)
        self.arithmetic_reasoning = operator.ArithmeticReasoning(self.config, self.problem)
        self.comparison_reasoning = operator.ComparisonReasoning(self.config, self.problem)
        self.flexible_custom = operator.FlexibleCustom(self.config, self.problem)

    async def run_workflow(self):
        """
        This is a workflow graph optimized for reading comprehension and discrete reasoning.
        It leverages specialized operators based on problem type and ensembles results for robustness.
        """
        # Step 1: Use Custom to extract and reason step-by-step from the passage
        initial_reasoning = await self.custom(instruction="Break down the problem into smaller steps and explain the reasoning behind each step clearly.")

        # Step 2: Generate direct answer using AnswerGenerate for baseline
        direct_answer = await self.answer_generate()

        # Step 3: Ensemle multiple solutions — one from direct generation, one from custom reasoning
        ensemble_candidates = [initial_reasoning, direct_answer]
        ensembled_solution = await self.sc_ensemble(solutions=ensemble_candidates)

        # Step 4: Review the ensembled solution for refinement
        refined_solution = await self.review(pre_solution=ensembled_solution)

        # Step 5: If problem involves counting, use CountingReasoning as an additional check
        count_result = await self.counting_reasoning()

        # Step 6: If arithmetic is involved, verify with ArithmeticReasoning
        arithmetic_result = await self.arithmetic_reasoning()

        # Step 7: If comparison is needed (e.g., min/max), use ComparisonReasoning
        comparison_result = await self.comparison_reasoning()

        # Final ensemble: combine all outputs to get the most reliable answer
        final_candidates = [
            refined_solution,
            count_result,
            arithmetic_result,
            comparison_result
        ]
        
        final_answer = await self.sc_ensemble(solutions=final_candidates)

        return final_answer