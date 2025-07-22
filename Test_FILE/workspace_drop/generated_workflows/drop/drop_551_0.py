# Workflow ID: drop_551_0
# Benchmark: drop
# Data Indices: [3349, 2983, 1714, 1428]

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
        Uses step-by-step breakdowns, specialized operators for task types, and ensembling for robustness.
        """
        # Step 1: Break down the problem logically using Custom
        reasoning_step = await self.custom(instruction="Can you solve this problem by breaking it down into detailed steps and explaining the reasoning behind each step?")
        
        # Step 2: Use flexible custom for structured reasoning (sequential + iterative refinement)
        structured_solution = await self.flexible_custom(
            custom_instruction="Focus on careful extraction of key facts and logical sequencing",
            reasoning_pattern="sequential",
            steps=["extract_key_events", "order_events", "verify_sequence"]
        )
        
        # Step 3: Generate direct answer using AnswerGenerate
        direct_answer = await self.answer_generate()
        
        # Step 4: Review the initial solution for accuracy
        reviewed_solution = await self.review(pre_solution=structured_solution)
        
        # Step 5: Ensemble multiple solutions for final selection
        ensemble_candidates = [direct_answer, reviewed_solution, reasoning_step]
        final_solution = await self.sc_ensemble(solutions=ensemble_candidates)
        
        return final_solution