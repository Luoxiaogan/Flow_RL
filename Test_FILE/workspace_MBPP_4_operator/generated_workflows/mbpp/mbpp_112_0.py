# Workflow ID: mbpp_112_0
# Benchmark: mbpp
# Data Indices: [91]

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

        # Step 1: Analyze the problem
        analysis = await self.generate(
            instruction="""Analyze the problem description:
            - Classify the problem type (e.g., list operations, math computations)
            - Identify key requirements and constraints
            - Extract the function name from test cases
            - Note any edge cases or special conditions
            Provide a structured breakdown.""",
            context=""
        )

        # Step 2: Generate multiple candidate solutions in parallel
        candidates = await asyncio.gather(
            self.generate(
                instruction=f"""Solve the problem using an iterative approach:
                - Use loops and basic constructs
                - Avoid recursion
                - Include necessary imports
                - Ensure the function name matches the test cases
                Problem analysis: {analysis}""",
                context=""
            ),
            self.generate(
                instruction=f"""Solve the problem using a recursive approach:
                - Use recursion for computation
                - Avoid loops
                - Include necessary imports
                - Ensure the function name matches the test cases
                Problem analysis: {analysis}""",
                context=""
            ),
            self.generate(
                instruction=f"""Solve the problem using Python's standard library:
                - Leverage built-in functions and modules
                - Minimize custom logic
                - Include necessary imports
                - Ensure the function name matches the test cases
                Problem analysis: {analysis}""",
                context=""
            )
        )

        # Step 3: Select the best solution using ensemble
        selected_solution = await self.ensemble(
            instruction="""Evaluate the candidate solutions:
            - Check correctness against test cases
            - Assess clarity and readability
            - Consider computational efficiency
            - Prefer solutions using standard library when equivalent
            Select the best solution.""",
            contexts_list=candidates
        )

        # Step 4: Iterative refinement loop
        refined_solution = selected_solution
        for _ in range(3):  # Maximum of 3 refinement iterations
            validation = await self.generate(
                instruction=f"""Validate the solution against the test cases:
                - Check if all assertions pass
                - Identify any errors or edge cases
                - Provide feedback for improvement
                Solution: {refined_solution}""",
                context=refined_solution
            )
            if "error" not in validation.lower():
                break  # Exit loop if no errors
            refined_solution = await self.revise(
                instruction=f"""Revise the solution based on validation feedback:
                - Fix identified issues
                - Improve clarity and correctness
                - Ensure all test cases pass
                Feedback: {validation}""",
                context=refined_solution
            )

        # Step 5: Generate final Python code
        final_code = await self.generate(
            instruction=f"""Generate the final Python code:
            - Use proper indentation (4 spaces)
            - Include all necessary imports at the top
            - Ensure the function name matches the test cases
            - Format the code as a markdown code block
            Refined solution: {refined_solution}""",
            context=refined_solution
        )

        return final_code