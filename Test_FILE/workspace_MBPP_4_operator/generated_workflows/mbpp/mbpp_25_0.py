# Workflow ID: mbpp_25_0
# Benchmark: mbpp
# Data Indices: [302, 273]

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
        import re

        # Step 1: Extract function name from test cases
        function_name_context = await self.generate(
            instruction="""Extract the function name from the test cases. 
            Look for patterns like 'assert function_name(args) == expected_output'.
            Return only the function name.""",
            context=""
        )
        function_name = re.search(r'([a-zA-Z_][a-zA-Z0-9_]*)', function_name_context).group(0)

        # Step 2: Understand task requirements
        task_understanding = await self.generate(
            instruction=f"""Interpret the task description in detail. 
            Focus on the following:
            - What is the input?
            - What is the output?
            - What is the relationship between input and output?
            - Are there any constraints or special conditions?""",
            context=""
        )
        refined_understanding = await self.revise(
            instruction=f"""Refine the task understanding to ensure it aligns with the test cases.
            Cross-check with the extracted function name: {function_name}.
            Clarify any ambiguities.""",
            context=task_understanding
        )

        # Step 3: Generate initial code
        initial_code = await self.generate(
            instruction=f"""Generate Python code for the function '{function_name}' based on the refined understanding.
            Ensure the code:
            - Includes all necessary imports
            - Follows proper indentation (4 spaces)
            - Passes the provided test cases""",
            context=refined_understanding
        )

        # Step 4: Validate and refine iteratively
        max_iterations = 5
        current_code = initial_code
        for i in range(max_iterations):
            validation = await self.generate(
                instruction=f"""Validate the following code against the test cases:
                {current_code}
                
                Identify any errors or mismatches. Provide detailed feedback.""",
                context=""
            )
            if "error" not in validation.lower():
                break  # Exit loop if no errors are found
            current_code = await self.revise(
                instruction=f"""Revise the code to fix the following issues:
                {validation}
                
                Ensure the revised code passes all test cases.""",
                context=current_code
            )

        # Step 5: Finalize solution
        final_solution = await self.summarize(
            instruction=f"""Condense the final solution into a clean, executable format.
            Ensure the code is complete and ready to run.""",
            context=current_code
        )

        return final_solution