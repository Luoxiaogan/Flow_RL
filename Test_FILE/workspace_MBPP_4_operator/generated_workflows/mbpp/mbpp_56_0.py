# Workflow ID: mbpp_56_0
# Benchmark: mbpp
# Data Indices: [24]

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
        
        # Step 1: Classify the problem type
        classification = await self.generate(
            instruction="""Classify the problem type based on the task description:
            - Is it a list/array operation, mathematical computation, string manipulation, etc.?
            - Identify key verbs and nouns that indicate the problem type.
            - Provide a structured classification.""",
            context=""
        )
        
        # Step 2: Extract the function name from assert statements
        function_name = await self.generate(
            instruction="""Extract the function name from the assert statements:
            - Look for the function name on the left-hand side of the assert statements.
            - Ensure the name is consistent across all test cases.
            - Return only the function name.""",
            context=classification
        )
        
        # Step 3: Parse the task description for requirements
        requirements = await self.generate(
            instruction=f"""Analyze the task description to identify requirements:
            - What actions need to be performed (e.g., swap, compute, find)?
            - What are the inputs and outputs?
            - Are there any constraints or special conditions?
            Classification: {classification}
            Function Name: {function_name}""",
            context=classification
        )
        
        # Step 4: Identify edge cases
        edge_cases = await self.generate(
            instruction=f"""Identify edge cases based on the task description and test cases:
            - What are the smallest or largest possible inputs?
            - Are there any special conditions (e.g., empty lists, single-element lists)?
            Requirements: {requirements}""",
            context=requirements
        )
        
        # Step 5: Generate initial code
        initial_code = await self.generate(
            instruction=f"""Generate Python code to solve the problem:
            - Use the function name: {function_name}.
            - Implement the logic based on the requirements: {requirements}.
            - Handle edge cases: {edge_cases}.
            - Include necessary imports at the top of the code.
            - Ensure proper indentation (4 spaces).""",
            context=edge_cases
        )
        
        # Step 6: Validate and refine the code
        for _ in range(3):  # Allow up to 3 refinement iterations
            validation = await self.generate(
                instruction=f"""Validate the generated code against the test cases:
                - Does the code pass all assert statements?
                - If not, identify errors or missing details.
                Code: {initial_code}""",
                context=initial_code
            )
            
            if "error" not in validation.lower():
                break  # Exit loop if code is valid
            
            initial_code = await self.revise(
                instruction=f"""Revise the code to fix issues:
                - Address errors identified in validation: {validation}.
                - Ensure the code remains clear and concise.
                Current Code: {initial_code}""",
                context=initial_code
            )
        
        return initial_code