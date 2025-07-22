# Workflow ID: drop_8_0
# Benchmark: drop
# Data Indices: [49, 1320, 583, 3977, 858]

class Workflow:
    def __init__(
        self,
        config,
        problem
    ) -> None:
        self.problem = problem
        self.agent = create(config)
        self.custom = operator.Custom(self.agent, self.problem)
        self.sc_ensemble = operator.ScEnsemble(self.agent, self.problem)
        self.answer_generate = operator.AnswerGenerate(self.agent, self.problem)
        self.review = operator.Review(self.agent, self.problem)
        self.counting_reasoning = operator.CountingReasoning(self.agent, self.problem)
        self.arithmetic_reasoning = operator.ArithmeticReasoning(self.agent, self.problem)
        self.comparison_reasoning = operator.ComparisonReasoning(self.agent, self.problem)
        self.flexible_custom = operator.FlexibleCustom(self.agent, self.problem)

    async def run_workflow(self):
        """
        This is a workflow graph optimized for iterative improvement.
        Starts with direct answer generation, then refines via review,
        and optionally uses specialized reasoning if needed based on problem type.
        """
        # Step 1: Generate initial solution
        initial_solution = await self.answer_generate()

        # Step 2: Review the initial solution to refine it
        refined_solution = await self.review(pre_solution=initial_solution)

        # Step 3: If problem involves counting, use counting reasoning
        count_result = await self.counting_reasoning()
        if "count" in refined_solution.lower() or "how many" in refined_solution.lower():
            final_solution = await self.sc_ensemble(solutions=[refined_solution, count_result])
        else:
            # Step 4: If arithmetic is needed, use arithmetic reasoning
            arithmetic_result = await self.arithmetic_reasoning()
            if any(op in refined_solution.lower() for op in ["add", "subtract", "multiply", "sum", "total"]):
                final_solution = await self.sc_ensemble(solutions=[refined_solution, arithmetic_result])
            else:
                # Step 5: If comparison is needed, use comparison reasoning
                comparison_result = await self.comparison_reasoning()
                if any(comp in refined_solution.lower() for comp in ["who has more", "longest", "shortest", "highest", "lowest"]):
                    final_solution = await self.sc_ensemble(solutions=[refined_solution, comparison_result])
                else:
                    # Step 6: Use flexible custom for complex discrete reasoning
                    flexible_result = await self.flexible_custom(
                        custom_instruction="Break down the problem step-by-step and reason carefully",
                        reasoning_pattern="sequential",
                        steps=["understand_question", "extract_evidence", "reason_step_by_step", "verify_answer"]
                    )
                    final_solution = await self.sc_ensemble(solutions=[refined_solution, flexible_result])

        return final_solution