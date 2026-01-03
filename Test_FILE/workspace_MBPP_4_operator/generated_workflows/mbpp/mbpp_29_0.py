# Workflow ID: mbpp_29_0
# Benchmark: mbpp
# Data Indices: [176]

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

        # Step 1: Problem Analysis
        analysis = await self.generate(
            instruction="""Extract the function name, parameters, and expected behavior from the test cases.
            Classify the problem into one of the following categories:
            - List/Array Operations
            - Mathematical Computations
            - String Manipulation
            - Data Structures
            - Standard Library Usage
            Identify any implicit constraints or edge cases.
            Format the output as structured text.""",
            context=""
        )

        # Step 2: Solution Generation
        solution = await self.generate(
            instruction=f"""Based on the analysis:
            {analysis}
            
            Generate Python code for the function. Ensure:
            - All necessary imports are included
            - The code adheres to the required format
            - Edge cases are handled appropriately
            Provide the complete code block.""",
            context=analysis
        )

        # Step 3: Validation
        validation = await self.generate(
            instruction=f"""Validate the following solution against the test cases:
            {solution}
            
            Check if the code passes all assertions. If not, identify the errors and suggest corrections.""",
            context=solution
        )

        # Step 4: Refinement (if needed)
        if "error" in validation.lower():
            refined_solution = await self.revise(
                instruction=f"""Revise the solution based on the following feedback:
                {validation}
                
                Address any errors, ambiguities, or inefficiencies. Ensure the code passes all test cases.""",
                context=solution
            )
            solution = refined_solution

        # Step 5: Final Output
        final_output = await self.summarize(
            instruction="""Condense the final solution into a clean and concise format.
            Ensure:
            - Proper indentation (4 spaces per level)
            - All necessary imports are included
            - The code adheres to Python conventions""",
            context=solution
        )

        return final_output