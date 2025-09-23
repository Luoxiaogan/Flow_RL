# Workflow ID: mbpp_53_0
# Benchmark: mbpp
# Data Indices: [319]

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
        # Extract function name from test cases
        function_name_context = await self.generate(
            instruction="""Extract the function name from the assert statements in the test cases.
            Look for the first word before an opening parenthesis in each assert statement.
            Return the function name as a single string.""",
            context=""
        )
        function_name_match = re.search(r"(\w+)\(", function_name_context)
        function_name = function_name_match.group(1) if function_name_match else "unknown_function"

        # Parse task description to identify key components
        task_analysis = await self.generate(
            instruction=f"""Analyze the task description to identify:
            - Input types and formats
            - Output requirements
            - Operations to perform
            - Any necessary imports from the Python standard library
            Function name: {function_name}
            Provide a structured summary.""",
            context=""
        )

        # Generate initial code solution
        initial_code = await self.generate(
            instruction=f"""Based on the task analysis:
            {task_analysis}
            
            Generate Python code with the following structure:
            - Include all necessary imports
            - Define a function named '{function_name}'
            - Implement the logic to solve the task
            Ensure the code is complete and executable.""",
            context=task_analysis
        )

        # Validate code against test cases
        validation_feedback = await self.generate(
            instruction=f"""Validate the generated code against the provided test cases.
            Identify any discrepancies between expected and actual outputs.
            Provide detailed feedback on errors or mismatches.
            Code:
            {initial_code}""",
            context=task_analysis
        )

        # Iterative refinement loop
        max_iterations = 3
        refined_code = initial_code
        for i in range(max_iterations):
            if "error" not in validation_feedback.lower() and "mismatch" not in validation_feedback.lower():
                break  # Exit loop if validation passes
            
            # Revise code based on validation feedback
            refined_code = await self.revise(
                instruction=f"""Revise the code to address the following issues:
                {validation_feedback}
                
                Ensure the revised code is complete and passes all test cases.""",
                context=refined_code
            )
            
            # Revalidate the revised code
            validation_feedback = await self.generate(
                instruction=f"""Validate the revised code against the provided test cases.
                Identify any remaining discrepancies.
                Code:
                {refined_code}""",
                context=task_analysis
            )

        # Finalize and return the solution
        final_solution = await self.revise(
            instruction="Ensure the final code is clean, well-formatted, and fully functional.",
            context=refined_code
        )
        return final_solution