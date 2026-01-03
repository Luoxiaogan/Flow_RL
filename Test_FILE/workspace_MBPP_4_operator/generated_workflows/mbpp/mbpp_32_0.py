# Workflow ID: mbpp_32_0
# Benchmark: mbpp
# Data Indices: [51]

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

        # Phase 1: Initial Analysis
        # Extract function name from test cases
        function_name_task = self.generate(
            instruction="""Extract the function name from the assert statements in the test cases.
            Look for patterns like 'assert function_name(args)' and return only the function name.
            Ensure the function name matches exactly as it appears in the test cases.""",
            context=""
        )
        
        # Parse task description for key operations and constraints
        task_description_task = self.generate(
            instruction="""Analyze the task description to identify:
            - Input types (e.g., list, tuple, string)
            - Operations to perform (e.g., flatten, sum, filter)
            - Expected output format
            Provide a structured summary of these components.""",
            context=""
        )
        
        # Run both tasks in parallel
        function_name_result, task_description_result = await asyncio.gather(function_name_task, task_description_task)
        
        # Extract function name using regex
        function_name_match = re.search(r"def\s+(\w+)\(", function_name_result)
        function_name = function_name_match.group(1) if function_name_match else "unknown_function"
        
        # Phase 2: Code Generation
        code_generation_task = self.generate(
            instruction=f"""Generate Python code for the function named '{function_name}'.
            Use the following task description: {task_description_result}
            Ensure the code:
            - Includes necessary imports
            - Handles edge cases
            - Passes the provided test cases
            Return the complete code with proper indentation.""",
            context=""
        )
        
        # Phase 3: Validation
        initial_code = await code_generation_task
        validation_task = self.generate(
            instruction=f"""Validate the following code against the test cases:
            {initial_code}
            Check if it passes all assertions. If it fails, identify the cause of failure.
            Return 'PASS' if successful, otherwise describe the issue.""",
            context=""
        )
        
        validation_result = await validation_task
        
        # Phase 4: Iterative Refinement
        while "PASS" not in validation_result.upper():
            refined_code = await self.revise(
                instruction=f"""Refine the following code to fix the issue:
                Issue: {validation_result}
                Code: {initial_code}
                Ensure the refined code passes all test cases.""",
                context=initial_code
            )
            initial_code = refined_code
            validation_result = await self.generate(
                instruction=f"""Re-validate the refined code:
                {refined_code}
                Return 'PASS' if successful, otherwise describe the issue.""",
                context=""
            )
        
        # Phase 5: Final Output
        final_summary = await self.summarize(
            instruction="""Summarize the final solution:
            - Function name
            - Key operations
            - Edge cases handled
            - Test case results""",
            context=initial_code
        )
        
        return f"{final_summary}\n\nGenerated Code:\n{initial_code}"