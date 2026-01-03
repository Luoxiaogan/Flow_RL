# Workflow ID: drop_63_0
# Benchmark: drop
# Data Indices: [404, 114]

class Workflow:
    def __init__(self, config, problem) -> None:
        self.config = config
        self.problem_text = problem
        self.llm = create(config)
        
        self.generate = operator.Generate(self.llm, self.problem_text)
        self.revise = operator.Revise(self.llm, self.problem_text)
        self.summarize = operator.Summarize(self.llm, self.problem_text)
        self.ensemble = operator.Ensemble(self.llm, self.problem_text)

    async def run_workflow(self):
        import asyncio

        # Step 1: Initial Analysis - Extract key information and classify problem type
        initial_analysis = await self.generate(
            instruction="""Extract all entities, numbers, and relationships from the passage.
            Classify the problem type based on the question:
            - Arithmetic: Addition, subtraction, etc.
            - Counting: Tally occurrences.
            - Comparison: Compare values.
            - Span Extraction: Find exact text spans.
            - Multi-step: Combine multiple operations.
            Provide structured output.""",
            context=""
        )

        # Step 2: Parallel Forks - Generate multiple solution attempts
        arithmetic_solution = await self.generate(
            instruction=f"""If this is an arithmetic problem, solve it:
            - Extract relevant numbers.
            - Perform the required operation.
            - Show all steps.
            Context: {initial_analysis}""",
            context=initial_analysis
        )
        counting_solution = await self.generate(
            instruction=f"""If this is a counting problem, solve it:
            - Identify the target entity/event.
            - Count all instances.
            - Show all steps.
            Context: {initial_analysis}""",
            context=initial_analysis
        )
        comparison_solution = await self.generate(
            instruction=f"""If this is a comparison problem, solve it:
            - Identify the values to compare.
            - Determine their relationship.
            - Show all steps.
            Context: {initial_analysis}""",
            context=initial_analysis
        )
        span_extraction_solution = await self.generate(
            instruction=f"""If this is a span extraction problem, solve it:
            - Locate the exact text span.
            - Ensure it matches the passage exactly.
            Context: {initial_analysis}""",
            context=initial_analysis
        )
        multi_step_solution = await self.generate(
            instruction=f"""If this is a multi-step problem, solve it:
            - Break into sub-problems.
            - Solve each sub-problem.
            - Combine results.
            Context: {initial_analysis}""",
            context=initial_analysis
        )

        # Step 3: Conditional Branching - Select the most appropriate solution
        solutions = [arithmetic_solution, counting_solution, comparison_solution, span_extraction_solution, multi_step_solution]
        selected_solution = await self.ensemble(
            instruction="""Select the best solution based on:
            - Relevance to the problem type.
            - Completeness of reasoning.
            - Accuracy of execution.""",
            contexts_list=solutions
        )

        # Step 4: Iterative Refinement - Validate and refine the solution
        refined_solution = selected_solution
        for _ in range(3):  # Allow up to 3 refinement iterations
            validation = await self.generate(
                instruction=f"""Validate the solution:
                - Check for errors.
                - Verify intermediate steps.
                - Confirm final answer matches expected format.
                Solution: {refined_solution}""",
                context=initial_analysis
            )
            if "error" in validation.lower():
                refined_solution = await self.revise(
                    instruction=f"""Fix errors identified in validation:
                    - Correct mistakes.
                    - Clarify reasoning.
                    Validation: {validation}""",
                    context=refined_solution
                )
            else:
                break

        # Step 5: Final Synthesis - Format the answer
        final_answer = await self.generate(
            instruction=f"""Format the final answer:
            - Ensure it matches the expected format (number, date, or text span).
            - Remove any extraneous information.
            Refined Solution: {refined_solution}""",
            context=initial_analysis
        )

        return final_answer