# Workflow ID: drop_747_0
# Benchmark: drop
# Data Indices: [1481, 988, 1867, 3439]

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
        This is a workflow graph optimized for step-by-step reasoning in reading comprehension and discrete tasks.
        Uses specialized operators based on problem type and ensembles multiple solutions for robustness.
        """
        # Step 1: Use flexible custom to extract key entities and structure the problem
        structured_analysis = await self.flexible_custom(
            custom_instruction="Break down the problem into core elements: question, relevant passage segments, and key entities.",
            reasoning_pattern="sequential",
            steps=["extract_question", "identify_entities", "map_relations"]
        )

        # Step 2: Generate an initial answer using direct reasoning
        initial_answer = await self.answer_generate()

        # Step 3: Use comparison reasoning for problems involving ranking or selection (e.g., "who scored most")
        comparison_result = await self.comparison_reasoning()

        # Step 4: Use counting reasoning for problems requiring enumeration (e.g., "how many years")
        counting_result = await self.counting_reasoning()

        # Step 5: Use arithmetic reasoning for numerical computation (e.g., time spans, totals)
        arithmetic_result = await self.arithmetic_reasoning()

        # Step 6: Review the initial answer with a detailed thought process
        reviewed_answer = await self.review(pre_solution=initial_answer)

        # Step 7: Ensemble all generated solutions to select the best one
        solution_list = [initial_answer, reviewed_answer, comparison_result, counting_result, arithmetic_result]
        final_solution = await self.sc_ensemble(solutions=solution_list)

        return final_solution