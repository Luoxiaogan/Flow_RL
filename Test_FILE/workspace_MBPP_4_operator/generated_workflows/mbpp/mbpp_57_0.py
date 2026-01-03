# Workflow ID: mbpp_57_0
# Benchmark: mbpp
# Data Indices: [234]

import asyncio
import re

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
        import re  # Import necessary modules inside the method

        # Step 1: Extract function signature from test cases
        function_signature = await self.generate(
            instruction="""Extract the function name and argument structure from the test cases.
            - Look for patterns like 'assert function_name(args) == expected_output'.
            - Identify the function name and the number/types of arguments.
            - Return the function signature in the format 'def function_name(arg1, arg2, ...):'.""",
            context=""
        )

        # Step 2: Summarize task requirements
        task_summary = await self.summarize(
            instruction="""Summarize the task requirements from the natural language description.
            - Identify inputs, outputs, and operations.
            - Highlight any constraints or special conditions.
            - Provide a concise summary suitable for code generation.""",
            context=function_signature
        )

        # Step 3: Generate initial Python code
        initial_code = await self.generate(
            instruction=f"""Generate Python code based on the task summary:
            Task Summary: {task_summary}
            
            Instructions:
            - Write a complete function definition starting with {function_signature}.
            - Include all necessary imports at the top of the code.
            - Ensure proper indentation (4 spaces per level).
            - Handle edge cases mentioned in the summary.
            - Return syntactically correct and executable Python code.""",
            context=task_summary
        )

        # Step 4: Validate code against test cases
        validation_result = await self.generate(
            instruction=f"""Validate the generated code against the provided test cases:
            Generated Code: {initial_code}
            
            Instructions:
            - Simulate the execution of the code with the test case inputs.
            - Compare the outputs with the expected results.
            - Identify any failures and their causes.
            - Return a report detailing success/failure and reasons for any failures.""",
            context=initial_code
        )

        # Step 5: Revise code if validation fails
        if "failure" in validation_result.lower():
            revised_code = await self.revise(
                instruction=f"""Revise the code to address the following issues:
                Validation Report: {validation_result}
                
                Instructions:
                - Fix logical errors or missing edge cases.
                - Maintain proper syntax and indentation.
                - Ensure the revised code satisfies all test cases.""",
                context=initial_code
            )
        else:
            revised_code = initial_code

        # Step 6: Ensemble to finalize the best solution
        final_code = await self.ensemble(
            instruction="""Select the best version of the code from multiple iterations:
            - Prioritize solutions that pass all test cases.
            - Choose the most readable and efficient implementation.
            - Ensure the final code is complete and executable.""",
            contexts_list=[initial_code, revised_code]
        )

        return final_code