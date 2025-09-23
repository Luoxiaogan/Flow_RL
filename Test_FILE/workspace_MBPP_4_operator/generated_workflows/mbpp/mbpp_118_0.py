# Workflow ID: mbpp_118_0
# Benchmark: mbpp
# Data Indices: [17]

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
        
        # Step 1: Extract Function Name
        function_name_extraction = await self.generate(
            instruction="""Extract the function name from the assert statements. 
            Ensure you capture the exact name used in the test cases. 
            Format your response as: FUNCTION_NAME""",
            context=""
        )
        function_name = re.search(r'FUNCTION_NAME\s*:\s*(\w+)', function_name_extraction).group(1)
        
        # Step 2: Parse Natural Language Description
        task_analysis = await self.generate(
            instruction=f"""Analyze the task description to identify key requirements:
            Task Description: {self.problem_text}
            
            Identify:
            - Required operations (e.g., map, filter, reduce)
            - Specific Python constructs or libraries mentioned
            - Any constraints or conditions stated
            - Expected input/output types
            
            Provide structured analysis.""",
            context=""
        )
        
        # Step 3: Generate Initial Code Solution
        initial_code = await self.generate(
            instruction=f"""Based on the following analysis, generate Python code:
            Function Name: {function_name}
            Task Analysis: {task_analysis}
            
            Ensure:
            - Proper imports are included
            - Correct function signature is used
            - Code is syntactically correct and well-indented
            - All requirements from the task analysis are addressed
            
            Format your response as a complete Python code block.""",
            context=task_analysis
        )
        
        # Step 4: Refine Code Solution
        refined_code = await self.revise(
            instruction=f"""Review and refine the following code:
            {initial_code}
            
            Focus on:
            - Improving clarity and readability
            - Adding missing details or edge case handling
            - Ensuring compliance with best coding practices
            - Maintaining alignment with the task requirements
            
            Return the improved code.""",
            context=initial_code
        )
        
        # Step 5: Validate Against Test Cases
        validation_result = await self.generate(
            instruction=f"""Validate the following code against the provided test cases:
            Code: {refined_code}
            
            Ensure:
            - All assert statements pass successfully
            - Edge cases are handled appropriately
            - The function behaves as expected for given examples
            
            If validation fails, provide detailed feedback on issues encountered.""",
            context=refined_code
        )
        
        # Conditional Branch: Handle Validation Feedback
        if "error" in validation_result.lower() or "fail" in validation_result.lower():
            final_code = await self.revise(
                instruction=f"""Address the following issues in the code:
                Issues: {validation_result}
                
                Make necessary corrections and return the fixed code.""",
                context=refined_code
            )
        else:
            final_code = refined_code
        
        # Step 6: Summarize Final Solution
        summary = await self.summarize(
            instruction=f"""Summarize the final solution:
            Code: {final_code}
            
            Include:
            - Key features of the solution
            - How it addresses the task requirements
            - Any notable edge cases handled
            
            Keep the summary concise yet informative.""",
            context=final_code
        )
        
        return {
            "function_name": function_name,
            "final_code": final_code,
            "summary": summary
        }