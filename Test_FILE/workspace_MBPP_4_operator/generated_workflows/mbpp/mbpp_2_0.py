# Workflow ID: mbpp_2_0
# Benchmark: mbpp
# Data Indices: [314]

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

        # Step 1: Initial Analysis (Parallel Fork)
        # Extract function name from assert statements
        func_name_extraction = await self.generate(
            instruction="""Extract the function name from the assert statements. 
            Look for patterns like 'assert function_name(args) == expected_output'.
            Return only the function name without additional commentary.""",
            context=""
        )

        # Classify problem type and identify key requirements
        problem_analysis = await self.generate(
            instruction="""Analyze the task description and classify the problem type:
            - Is it a list/array operation, mathematical computation, string manipulation, etc.?
            - What are the key requirements? For example, sorting logic, grouping criteria, etc.
            Provide a structured summary.""",
            context=""
        )

        # Identify potential edge cases from test cases
        edge_case_analysis = await self.generate(
            instruction="""Examine the test cases to identify potential edge cases:
            - What are the boundary conditions?
            - Are there any special cases like empty inputs, zeros, or extreme values?
            List the edge cases clearly.""",
            context=""
        )

        # Synthesize initial insights
        initial_insights = await self.ensemble(
            instruction="""Combine the extracted function name, problem classification, and edge cases into a unified understanding.
            Ensure all critical information is captured.""",
            contexts_list=[func_name_extraction, problem_analysis, edge_case_analysis]
        )

        # Step 2: Code Generation (Sequential Chain)
        # Generate initial code draft
        initial_code = await self.generate(
            instruction=f"""Based on the following insights:
            {initial_insights}
            
            Generate a complete Python function that satisfies the task description and passes all test cases.
            Include necessary imports at the top of the code.
            Ensure proper indentation and clean syntax.""",
            context=""
        )

        # Validate and refine the code iteratively
        refined_code = initial_code
        for _ in range(3):  # Limit iterations to prevent infinite loops
            validation = await self.generate(
                instruction=f"""Validate the following code against the test cases:
                {refined_code}
                
                Identify any issues, such as syntax errors, logical flaws, or missing edge cases.
                Provide detailed feedback.""",
                context=refined_code
            )
            if "error" in validation.lower() or "issue" in validation.lower():
                refined_code = await self.revise(
                    instruction=f"""Refine the code to address the following issues:
                    {validation}
                    
                    Ensure the updated code is correct and complete.""",
                    context=refined_code
                )
            else:
                break

        # Step 3: Validation and Finalization (Conditional Branch)
        final_validation = await self.generate(
            instruction=f"""Test the following code against all assert statements:
            {refined_code}
            
            Confirm whether the code passes all test cases.
            If any test case fails, provide detailed analysis of the failure.""",
            context=refined_code
        )

        if "fail" in final_validation.lower():
            final_code = await self.revise(
                instruction=f"""Fix the code to resolve the following issues:
                {final_validation}
                
                Ensure the final version is fully functional and passes all test cases.""",
                context=refined_code
            )
        else:
            final_code = refined_code

        return final_code