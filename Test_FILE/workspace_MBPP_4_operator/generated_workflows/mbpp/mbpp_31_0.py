# Workflow ID: mbpp_31_0
# Benchmark: mbpp
# Data Indices: [22]

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

        # Step 1: Extract function name and validate consistency
        function_name_extraction = await self.generate(
            instruction="""Extract the function name from the assert statements in the test cases.
            Ensure consistency across all test cases and validate the function signature.
            Format the result as 'Function Name: <name>'.""",
            context=""
        )
        function_name = re.search(r"Function Name: (\w+)", function_name_extraction).group(1)

        # Step 2: Parse natural language description and summarize requirements
        task_analysis = await self.generate(
            instruction="""Analyze the natural language task description to identify:
            - Input types and formats
            - Expected output
            - Constraints and edge cases
            Provide a detailed breakdown.""",
            context=""
        )
        summarized_requirements = await self.summarize(
            instruction="Condense the task analysis into a structured summary of key requirements.",
            context=task_analysis
        )

        # Step 3: Classify problem type and select strategy
        problem_classification = await self.generate(
            instruction=f"""Classify the problem based on the summarized requirements:
            {summarized_requirements}
            
            Possible categories include:
            - List/Array Operations
            - Mathematical Computations
            - String Manipulation
            - Data Structures
            - Standard Library Usage
            
            Select the most appropriate category and suggest a solution strategy.""",
            context=summarized_requirements
        )

        # Step 4: Generate initial solution
        initial_solution = await self.generate(
            instruction=f"""Generate Python code for the function '{function_name}' based on:
            - Summarized requirements: {summarized_requirements}
            - Problem classification: {problem_classification}
            
            Include necessary imports at the top of the code and ensure proper indentation.""",
            context=problem_classification
        )

        # Step 5: Refine solution for correctness and clarity
        refined_solution = await self.revise(
            instruction=f"""Refine the initial solution to ensure:
            - Correctness: Passes all test cases
            - Clarity: Readable and well-structured
            - Best Practices: Adheres to Python conventions
            
            Initial solution:
            {initial_solution}""",
            context=initial_solution
        )

        # Step 6: Validate against test cases and analyze edge cases
        validation_results = await asyncio.gather(
            *[self.generate(
                instruction=f"""Validate the refined solution against the test case:
                {test_case}
                
                Ensure the function produces the expected output.""",
                context=refined_solution
            ) for test_case in re.findall(r"assert .+", self.problem_text)]
        )
        edge_case_analysis = await self.generate(
            instruction=f"""Identify potential edge cases for the problem based on:
            - Summarized requirements: {summarized_requirements}
            - Problem classification: {problem_classification}
            
            Suggest additional test cases if necessary.""",
            context=refined_solution
        )

        # Step 7: Synthesize final assessment
        final_assessment = await self.ensemble(
            instruction="""Synthesize the validation results and edge case analysis into a final assessment:
            - Does the solution pass all test cases?
            - Are edge cases adequately handled?
            - Is the code robust and maintainable?""",
            contexts_list=validation_results + [edge_case_analysis]
        )

        return refined_solution, final_assessment