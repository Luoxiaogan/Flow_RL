# Workflow ID: mbpp_51_0
# Benchmark: mbpp
# Data Indices: [29, 330]

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
        
        # Step 1: Extract Function Signature
        function_info = await self.generate(
            instruction="""Extract the function name and parameters from the test cases.
            Format the result as:
            Function Name: <name>
            Parameters: <param1>, <param2>, ...
            Return Type: <type>""",
            context=""
        )
        
        # Step 2: Problem Classification
        classification = await self.generate(
            instruction="""Classify the problem into one of the following categories:
            - Mathematical Computation
            - List/Array Operations
            - String Manipulation
            - Data Structures
            - Standard Library Usage
            Provide reasoning for the classification.""",
            context=function_info
        )
        
        # Step 3: Generate Initial Solution
        initial_solution = await self.generate(
            instruction=f"""Based on the classification: {classification}
            Generate an initial Python solution including necessary imports.
            Ensure proper indentation and complete function definition.""",
            context=function_info
        )
        
        # Step 4: Validation and Refinement Loop
        max_iterations = 5
        for i in range(max_iterations):
            validation = await self.generate(
                instruction=f"""Validate the following solution against the test cases:
                {initial_solution}
                Identify any errors or improvements needed.""",
                context=function_info
            )
            
            if "error" in validation.lower():
                initial_solution = await self.revise(
                    instruction=f"""Refine the solution based on the following feedback:
                    {validation}
                    Ensure the refined solution addresses all issues.""",
                    context=initial_solution
                )
            else:
                break
        
        # Step 5: Final Output
        final_code = await self.generate(
            instruction=f"""Format the final solution for output:
            {initial_solution}
            Ensure it is clean, properly indented, and includes all necessary imports.""",
            context=""
        )
        
        return final_code