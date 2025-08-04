# Workflow ID: drop_0_1
# Benchmark: drop
# Data Indices: [1, 0]

class Workflow:
    def __init__(
        self,
        config,
        problem
    ) -> None:
        # --- DO NOT MODIFY THIS SECTION ---
        self.config = config
        self.problem = problem
        self.problem_text = str(problem) if isinstance(problem, dict) else problem
        
        # Create LLM instance from config
        self.llm = create(self.config)

        # All available operators are initialized here for your use.
        self.custom = operator.Custom(self.llm, self.problem)
        self.counting_reasoning = operator.CountingReasoning(self.llm, self.problem)
        self.arithmetic_reasoning = operator.ArithmeticReasoning(self.llm, self.problem)
        self.comparison_reasoning = operator.ComparisonReasoning(self.llm, self.problem)
        self.review = operator.Review(self.llm, self.problem)
        self.sc_ensemble = operator.ScEnsemble(self.llm, self.problem)
        self.flexible_custom = operator.FlexibleCustom(self.llm, self.problem)

    async def run_workflow(self):
        """
        This is where you implement the core problem-solving logic.
        You can use any of the operators initialized above.
        """
        # Step 1: Use FlexibleCustom to define a multi-step reasoning pattern
        reasoning_steps = [
            "Identify the question and extract all relevant numerical values from the passage.",
            "Determine the type of reasoning required (e.g., arithmetic, counting, comparison).",
            "Apply the appropriate reasoning operator based on the task.",
            "Validate the result and refine if necessary."
        ]
        
        reasoning_pattern = "Sequential reasoning: Break down the problem step-by-step and solve it incrementally."
        
        initial_analysis = await self.flexible_custom(
            reasoning_pattern=reasoning_pattern,
            steps=reasoning_steps,
            custom_instruction="Analyze the passage and identify the main question. Extract all numerical values and key events related to the question."
        )
        
        # Step 2: Use the extracted information to perform the specific task
        if "arithmetic" in initial_analysis.lower():
            final_result = await self.arithmetic_reasoning()
        elif "counting" in initial_analysis.lower():
            final_result = await self.counting_reasoning()
        elif "comparison" in initial_analysis.lower():
            final_result = await self.comparison_reasoning()
        else:
            final_result = await self.custom(instruction="Based on the analysis, solve the problem directly.")
        
        # Step 3: Review and refine the solution
        refined_solution = await self.review(pre_solution=final_result)
        
        return refined_solution