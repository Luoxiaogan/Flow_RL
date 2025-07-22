# Workflow ID: drop_214_0
# Benchmark: drop
# Data Indices: [2021, 695, 2693, 195]

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
        This is a robust workflow graph using Parallel Ensemble for enhanced accuracy.
        Generates multiple solutions via different reasoning paths, then selects the best one.
        """
        # Generate multiple independent solutions using diverse reasoning strategies
        solution1 = await self.answer_generate()
        
        solution2 = await self.custom(instruction="Break down the problem step by step and explain each reasoning step clearly.")
        
        solution3 = await self.flexible_custom(
            custom_instruction="Use sequential reasoning to solve this problem carefully.",
            reasoning_pattern="sequential",
            steps=["extract_key_info", "identify_question_type", "apply_logic", "verify_solution"]
        )
        
        solution4 = await self.counting_reasoning()
        
        solution5 = await self.arithmetic_reasoning()
        
        solution6 = await self.comparison_reasoning()

        # Ensemble all solutions to select the most consistent and accurate one
        solutions = [solution1, solution2, solution3, solution4, solution5, solution6]
        final_answer = await self.sc_ensemble(solutions=solutions)

        return final_answer