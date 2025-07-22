# Workflow ID: drop_4_0
# Benchmark: drop
# Data Indices: [254, 577, 1945, 2999]

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
        This is a workflow graph optimized for iterative improvement.
        Starts with direct answer generation, then refines via review.
        Multiple solutions are generated and ensembled for robustness.
        """
        # Step 1: Generate initial solution directly
        initial_solution = await self.answer_generate()

        # Step 2: Review the initial solution to refine it
        refined_solution = await self.review(pre_solution=initial_solution)

        # Step 3: Generate alternative reasoning paths using custom prompts
        step_by_step_solution = await self.custom(instruction="Break down the problem into smaller steps and explain the reasoning behind each step.")
        
        # Step 4: Use flexible custom for structured iterative refinement (e.g., count or compare)
        iterative_solution = await self.flexible_custom(
            custom_instruction="Use an iterative approach to verify the answer step by step.",
            reasoning_pattern="iterative",
            steps=["identify_key_elements", "extract_values", "validate_logic", "refine_answer"],
            max_iterations=2
        )

        # Step 5: Ensemble multiple solutions for final decision
        solutions = [initial_solution, refined_solution, step_by_step_solution, iterative_solution]
        final_solution = await self.sc_ensemble(solutions=solutions)

        return final_solution