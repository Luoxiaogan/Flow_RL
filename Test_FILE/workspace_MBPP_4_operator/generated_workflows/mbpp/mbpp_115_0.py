# Workflow ID: mbpp_115_0
# Benchmark: mbpp
# Data Indices: [218]

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

        # Initial analysis and classification
        analysis = await self.generate(
            instruction="""Classify the problem based on its description:
            - Identify the primary operation (list, math, string, etc.)
            - Note any specific requirements or constraints
            - Highlight expected output format and edge cases""",
            context=""
        )

        # Extract function name from assert statements
        function_name_extraction = await self.generate(
            instruction="""Extract the function name from the assert statements:
            - Use pattern matching to find 'assert function_name(...)'
            - Ensure the extracted name is valid and matches test cases""",
            context=analysis
        )

        # Validate and clean function name extraction
        function_name = re.search(r'assert\s+(\w+)\(', function_name_extraction)
        function_name = function_name.group(1) if function_name else "unknown_function"

        # Generate multiple solution attempts in parallel
        solutions = await asyncio.gather(
            self.generate(
                instruction=f"""Develop a solution focusing on core logic:
                - Follow the problem description: {analysis}
                - Use standard library functions where applicable
                - Ensure proper indentation and syntax""",
                context=""
            ),
            self.generate(
                instruction=f"""Develop an alternative solution emphasizing edge cases:
                - Address potential edge cases from: {analysis}
                - Include error handling and boundary checks""",
                context=""
            ),
            self.generate(
                instruction=f"""Create a comprehensive solution integrating both logic and edge cases:
                - Combine insights from previous analyses: {analysis}
                - Ensure completeness and robustness""",
                context=""
            )
        )

        # Synthesize the best solution from multiple attempts
        synthesized_solution = await self.ensemble(
            instruction="""Select the most effective solution:
            - Evaluate based on correctness, completeness, and clarity
            - Prefer solutions that handle edge cases well""",
            contexts_list=solutions
        )

        # Iterative refinement of the synthesized solution
        refined_solution = synthesized_solution
        for _ in range(3):  # Allow up to 3 refinement iterations
            validation = await self.generate(
                instruction=f"""Validate the current solution:
                - Check against provided test cases
                - Identify any issues or improvements needed""",
                context=refined_solution
            )
            if "error" in validation.lower() or "improve" in validation.lower():
                refined_solution = await self.revise(
                    instruction=f"""Refine the solution based on validation feedback:
                    - Address identified issues: {validation}
                    - Enhance clarity and correctness""",
                    context=refined_solution
                )
            else:
                break

        # Final validation and formatting
        final_code = await self.generate(
            instruction=f"""Ensure the final solution is complete and executable:
            - Include all necessary imports at the top
            - Format with proper indentation (4 spaces)
            - Define the function with the extracted name: {function_name}
            - Validate against all test cases""",
            context=refined_solution
        )

        return final_code