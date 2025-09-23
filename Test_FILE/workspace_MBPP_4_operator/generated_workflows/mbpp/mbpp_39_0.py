# Workflow ID: mbpp_39_0
# Benchmark: mbpp
# Data Indices: [242]

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

        # Step 1: Extract function name and key components
        initial_analysis = await self.generate(
            instruction="""Extract the function name from the assert statements and identify key components:
            - Function name appears in assert statements (e.g., `function_name(args)`)
            - Inputs and outputs from test cases
            - Any constraints or edge cases mentioned in the task description""",
            context=""
        )

        # Step 2: Analyze task description for operations and libraries
        task_decomposition = await self.generate(
            instruction=f"""Analyze the task description to infer required operations and libraries:
            Problem Text: {self.problem_text}
            Initial Analysis: {initial_analysis}
            
            Identify:
            - Required operations (e.g., list manipulation, mathematical computations)
            - Standard library functions or modules needed
            - Potential edge cases (e.g., empty inputs, large numbers)""",
            context=initial_analysis
        )

        # Step 3: Generate initial Python code
        code_generation = await self.generate(
            instruction=f"""Generate Python code based on the analysis:
            Function Name: Extracted from assert statements
            Operations: Identified from task description
            Libraries: Inferred from task requirements
            
            Ensure:
            - Proper imports
            - Correct indentation
            - Complete function definition""",
            context=task_decomposition
        )

        # Step 4: Validate and refine code
        validation_feedback = await self.generate(
            instruction=f"""Validate the generated code against test cases:
            Generated Code: {code_generation}
            
            Check:
            - All assert statements pass
            - Handle any edge cases missed in initial generation""",
            context=code_generation
        )

        # Step 5: Refine code based on validation feedback
        refined_code = await self.revise(
            instruction=f"""Refine the code based on validation feedback:
            Feedback: {validation_feedback}
            
            Fix:
            - Syntax errors
            - Logical mistakes
            - Missing edge case handling""",
            context=code_generation
        )

        # Final Output
        return refined_code