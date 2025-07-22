# Workflow ID: drop_223_0
# Benchmark: drop
# Data Indices: [2591, 3141, 160, 1483]

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
        It uses step-by-step reasoning with specialized operators and ensembles multiple solutions.
        """
        # Step 1: Generate initial answer using direct reasoning
        initial_answer = await self.answer_generate()

        # Step 2: Use Custom to extract key facts or break down the problem
        extracted_facts = await self.custom(instruction="Break down the problem into smaller steps and explain the reasoning behind each step.")

        # Step 3: Perform counting if needed (e.g., number of events, players, etc.)
        counting_result = await self.counting_reasoning()

        # Step 4: Perform arithmetic if needed (e.g., totals, differences, averages)
        arithmetic_result = await self.arithmetic_reasoning()

        # Step 5: Perform comparison if needed (e.g., max/min, relative values)
        comparison_result = await self.comparison_reasoning()

        # Step 6: Review the initial answer with feedback from other operators
        reviewed_answer = await self.review(pre_solution=initial_answer)

        # Step 7: Ensemble all solutions to select the best one
        solutions = [
            initial_answer,
            extracted_facts,
            counting_result,
            arithmetic_result,
            comparison_result,
            reviewed_answer
        ]
        final_answer = await self.sc_ensemble(solutions=solutions)

        return final_answer