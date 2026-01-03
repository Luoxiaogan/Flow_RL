# Workflow ID: mbpp_73_0
# Benchmark: mbpp
# Data Indices: [133, 148]

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

        # Step 1: Initial Analysis
        analysis = await self.generate(
            instruction="""Analyze the problem text to extract:
            - Task description: What is the task asking for?
            - Function name: Extract the function name from the test cases.
            - Input/Output patterns: Identify input types and expected outputs.
            - Constraints: List any explicit or implicit constraints.
            Provide this information in a structured format.""",
            context=""
        )

        # Extract function name using regex
        function_name_match = re.search(r"assert\s+(\w+)\(", analysis)
        function_name = function_name_match.group(1) if function_name_match else "unknown_function"

        # Step 2: Parallel Exploration of Approaches
        direct_solution, edge_case_handling, optimization = await asyncio.gather(
            self.generate(
                instruction=f"""Generate a direct implementation of the function '{function_name}' based on the task description:
                - Include necessary imports.
                - Ensure proper indentation and syntax.
                - Handle basic cases.""",
                context=analysis
            ),
            self.generate(
                instruction=f"""Focus on edge cases for the function '{function_name}':
                - Identify potential edge cases.
                - Modify the implementation to handle these cases.""",
                context=analysis
            ),
            self.generate(
                instruction=f"""Explore optimized solutions for the function '{function_name}':
                - Consider computational efficiency.
                - Use appropriate algorithms or data structures.""",
                context=analysis
            )
        )

        # Step 3: Synthesis and Validation
        synthesized_solution = await self.ensemble(
            instruction=f"""Synthesize the following approaches into a unified solution:
            - Direct implementation: {direct_solution}
            - Edge case handling: {edge_case_handling}
            - Optimization: {optimization}
            Ensure the final solution is complete, valid, and passes all test cases.""",
            contexts_list=[direct_solution, edge_case_handling, optimization]
        )

        # Validate the solution
        validation = await self.generate(
            instruction=f"""Validate the synthesized solution against the test cases:
            - Check if all test cases pass.
            - Identify any failing test cases and their reasons.
            Provide a summary of validation results.""",
            context=synthesized_solution
        )

        # Step 4: Iterative Refinement
        max_iterations = 5
        for _ in range(max_iterations):
            if "fail" not in validation.lower():
                break  # Solution is valid

            # Identify errors
            error_analysis = await self.generate(
                instruction=f"""Analyze why the solution failed validation:
                - Identify specific issues.
                - Suggest possible fixes.""",
                context=validation
            )

            # Revise the solution
            synthesized_solution = await self.revise(
                instruction=f"""Revise the solution based on the error analysis:
                - Fix identified issues.
                - Ensure the solution remains complete and valid.""",
                context=synthesized_solution
            )

            # Re-validate
            validation = await self.generate(
                instruction=f"""Re-validate the revised solution against the test cases:
                - Check if all test cases pass.
                - Identify any remaining issues.""",
                context=synthesized_solution
            )

        return synthesized_solution