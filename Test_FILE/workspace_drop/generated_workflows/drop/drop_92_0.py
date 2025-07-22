# Workflow ID: drop_92_0
# Benchmark: drop
# Data Indices: [27, 1203, 1852, 1500, 1151]

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
        This is a workflow graph using Parallel Ensemble for robustness.
        Generates multiple reasoning paths and selects the best answer via ScEnsemble.
        """
        # Generate multiple solutions using different reasoning approaches
        solution1 = await self.answer_generate()
        
        solution2 = await self.custom(instruction="Can you solve this problem by breaking it down into detailed steps and explaining the reasoning behind each step?")
        
        solution3 = await self.flexible_custom(
            custom_instruction="Use sequential reasoning to carefully analyze the passage step-by-step",
            reasoning_pattern="sequential",
            steps=["identify_key_events", "extract_entities", "determine_relationships", "formulate_answer"]
        )
        
        solution4 = await self.counting_reasoning()
        
        solution5 = await self.arithmetic_reasoning()
        
        solution6 = await self.comparison_reasoning()

        # Ensemble all solutions to select the most consistent one
        solutions = [solution1, solution2, solution3, solution4, solution5, solution6]
        final_answer = await self.sc_ensemble(solutions=solutions)

        return final_answer