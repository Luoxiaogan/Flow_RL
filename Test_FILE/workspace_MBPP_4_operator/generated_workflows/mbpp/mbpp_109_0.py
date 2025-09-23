# Workflow ID: mbpp_109_0
# Benchmark: mbpp
# Data Indices: [70]

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

        # Step 1: Extract function name from test cases
        function_name_extraction = await self.generate(
            instruction="""Extract the function name from the assert statements in the test cases.
            - Look for patterns like 'assert function_name(args) == expected_output'
            - Identify the function name precisely, including its casing and underscores
            - Return only the function name""",
            context=""
        )
        function_name = function_name_extraction.strip()

        # Step 2: Analyze the problem description
        problem_analysis = await self.generate(
            instruction=f"""Analyze the problem description to understand the requirements:
            - Problem Description: {self.problem_text}
            - Function Name: {function_name}
            
            Identify:
            - The type of problem (e.g., bitwise operation, string manipulation)
            - Key operations required
            - Potential edge cases
            - Any ambiguity in the description""",
            context=""
        )

        # Step 3: Generate multiple solution candidates
        candidates = await asyncio.gather(
            self.generate(
                instruction=f"""Generate a solution focusing on bitwise operations:
                - Problem Description: {self.problem_text}
                - Function Name: {function_name}
                - Key Insights: {problem_analysis}""",
                context=""
            ),
            self.generate(
                instruction=f"""Generate a solution focusing on mathematical transformations:
                - Problem Description: {self.problem_text}
                - Function Name: {function_name}
                - Key Insights: {problem_analysis}""",
                context=""
            ),
            self.generate(
                instruction=f"""Generate a solution using standard library functions:
                - Problem Description: {self.problem_text}
                - Function Name: {function_name}
                - Key Insights: {problem_analysis}""",
                context=""
            )
        )

        # Step 4: Validate and synthesize the best solution
        synthesis = await self.ensemble(
            instruction=f"""Evaluate the following candidate solutions and synthesize the best one:
            - Candidate 1: {candidates[0]}
            - Candidate 2: {candidates[1]}
            - Candidate 3: {candidates[2]}
            
            Criteria:
            - Correctness: Passes all test cases
            - Clarity: Easy to understand and well-structured
            - Efficiency: Minimal computational overhead""",
            contexts_list=candidates
        )

        # Step 5: Iterative refinement
        refined_solution = synthesis
        for _ in range(3):  # Limit iterations to avoid infinite loops
            validation = await self.generate(
                instruction=f"""Validate the solution against the test cases:
                - Solution: {refined_solution}
                - Test Cases: {self.problem_text}
                
                Identify any errors or missing edge cases.""",
                context=""
            )
            if "error" not in validation.lower():
                break  # Exit loop if no errors
            refined_solution = await self.revise(
                instruction=f"""Refine the solution to fix identified issues:
                - Issues: {validation}
                - Original Solution: {refined_solution}""",
                context=refined_solution
            )

        # Step 6: Finalize and format the output
        final_code = await self.generate(
            instruction=f"""Format the final solution as complete Python code:
            - Solution: {refined_solution}
            - Function Name: {function_name}
            
            Ensure:
            - All necessary imports are included
            - Code adheres to Python conventions (4-space indentation)
            - The function passes all test cases""",
            context=""
        )

        return final_code