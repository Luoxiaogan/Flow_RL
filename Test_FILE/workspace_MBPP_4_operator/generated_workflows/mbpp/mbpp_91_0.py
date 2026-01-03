# Workflow ID: mbpp_91_0
# Benchmark: mbpp
# Data Indices: [73, 325]

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

        # Step 1: Extract function name and parameters
        function_name_extraction = await self.generate(
            instruction="""Extract the function name and parameters from the test cases:
            - Identify the function name used in assert statements.
            - List all parameters passed to the function.
            Provide the results in the format: 'Function Name: <name>, Parameters: <params>'.""",
            context=""
        )
        match = re.search(r'Function Name: (\w+), Parameters: (.+)', function_name_extraction)
        function_name = match.group(1) if match else "unknown_function"
        parameters = match.group(2).split(", ") if match else []

        # Step 2: Classify problem type
        classification = await self.generate(
            instruction=f"""Classify the problem based on the task description:
            Task Description: {self.problem_text}
            
            Categories:
            - String Manipulation
            - Mathematical Computation
            - Data Structures
            - Standard Library Usage
            
            Provide the most likely category and reasoning.""",
            context=""
        )

        # Step 3: Parallel exploration of solutions
        candidate_solutions = await asyncio.gather(
            self.generate(
                instruction=f"""Generate a solution using list comprehensions:
                Function Name: {function_name}
                Parameters: {parameters}
                Task Description: {self.problem_text}""",
                context=""
            ),
            self.generate(
                instruction=f"""Generate a solution using loops:
                Function Name: {function_name}
                Parameters: {parameters}
                Task Description: {self.problem_text}""",
                context=""
            ),
            self.generate(
                instruction=f"""Generate a solution using standard library functions:
                Function Name: {function_name}
                Parameters: {parameters}
                Task Description: {self.problem_text}""",
                context=""
            )
        )

        # Step 4: Synthesize and refine the best solution
        best_solution = await self.ensemble(
            instruction=f"""Select the best solution based on clarity, correctness, and efficiency:
            Solutions:
            1. {candidate_solutions[0]}
            2. {candidate_solutions[1]}
            3. {candidate_solutions[2]}""",
            contexts_list=candidate_solutions
        )
        refined_solution = await self.revise(
            instruction="Improve clarity, add missing details, and ensure completeness.",
            context=best_solution
        )

        # Step 5: Validate and finalize
        validation_result = await self.generate(
            instruction=f"""Validate the solution against the test cases:
            Function Name: {function_name}
            Parameters: {parameters}
            Solution: {refined_solution}
            
            Check for:
            - Passing all test cases
            - Proper imports
            - Correct syntax and indentation""",
            context=""
        )
        if "error" in validation_result.lower():
            final_code = await self.revise(
                instruction=f"Fix issues identified during validation: {validation_result}",
                context=refined_solution
            )
        else:
            final_code = refined_solution

        return final_code