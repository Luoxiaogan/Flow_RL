# Workflow ID: mbppplus_26_0
# Benchmark: mbppplus
# Data Indices: [73, 68]

import asyncio

class Workflow:
    def __init__(self, config, problem) -> None:
        self.config = config
        self.problem_text = problem
        self.llm = create(config)
        
        self.generate = operator.Generate(self.llm, self.problem_text)
        self.revise = operator.Revise(self.llm, self.problem_text)
        self.summarize = operator.Summarize(self.llm, self.problem_text)
        self.ensemble = operator.Ensemble(self.llm, self.problem_text)
        self.programmer = operator.Programmer(self.llm, self.problem_text)
        self.decompose = operator.Decompose(self.llm, self.problem_text)

    async def run_workflow(self):
        import asyncio
        import re
        import json
        from collections import OrderedDict

        # Phase 1: Problem Decomposition and Classification
        decomposition = await self.decompose(
            instruction="""Thoroughly analyze this programming problem and break it down into essential components:
            1. Problem Category: Is this primarily about data transformation, validation, mathematical computation, or pattern matching?
            2. Input/Output Specification: What are the exact input types and expected output types? Are there format requirements?
            3. Edge Cases: Identify all potential edge cases (empty inputs, single elements, boundary values, invalid formats, etc.)
            4. Solution Approaches: List 2-3 different strategies that could solve this (algorithmic, regex-based, library-assisted, etc.)
            5. Constraints: Are there any performance, memory, or style constraints mentioned or implied?
            6. Test Cases: Generate 5-7 comprehensive test cases including edge cases that should be validated.
            Return this as a structured analysis with clear section headings.""",
            context=""
        )

        # Extract the structured analysis as context for next steps
        decomposition_summary = await self.summarize(
            instruction="Extract the key components from the decomposition: problem category, input/output specs, edge cases, and solution approaches. Format as concise bullet points.",
            context=str(decomposition)
        )

        # Phase 2: Parallel Solution Generation
        # Generate three different solution approaches in parallel
        solution_attempts = await asyncio.gather(
            self.generate(
                instruction=f"""Generate a pure algorithmic solution using basic Python constructs only:
                Problem Analysis: {decomposition_summary}
                
                Requirements:
                - Use only built-in Python features (no external libraries unless absolutely necessary)
                - Focus on clarity and step-by-step logic
                - Handle all identified edge cases explicitly
                - Match the exact function signature specified
                - Include all necessary imports within the function if needed
                - Return the correct data type as specified
                
                Provide ONLY the function implementation as specified in the output requirements.""",
                context=decomposition_summary
            ),
            self.generate(
                instruction=f"""Generate a solution leveraging appropriate Python libraries and built-ins:
                Problem Analysis: {decomposition_summary}
                
                Requirements:
                - Use the most suitable Python libraries or built-ins for this problem type (e.g., collections, re, itertools)
                - Optimize for efficiency and Pythonic style
                - Handle all identified edge cases
                - Match the exact function signature specified
                - Include all necessary imports at the top
                - Return the correct data type as specified
                
                Provide ONLY the function implementation as specified in the output requirements.""",
                context=decomposition_summary
            ),
            self.generate(
                instruction=f"""Generate a defensively coded solution with comprehensive edge case handling:
                Problem Analysis: {decomposition_summary}
                
                Requirements:
                - Prioritize robustness and error handling
                - Include explicit checks for all identified edge cases
                - Use try-except blocks where appropriate
                - Add input validation if the problem implies it
                - Match the exact function signature specified
                - Include all necessary imports at the top
                - Return the correct data type as specified
                - Include comments for complex logic
                
                Provide ONLY the function implementation as specified in the output requirements.""",
                context=decomposition_summary
            )
        )

        # Phase 3: Solution Synthesis
        synthesized_solution = await self.ensemble(
            instruction=f"""Synthesize the best solution from the three provided attempts:
            Problem Analysis: {decomposition_summary}
            
            Evaluation Criteria:
            1. Correctness: Does it handle all edge cases identified in the decomposition?
            2. Efficiency: Is it reasonably efficient for the problem size?
            3. Readability: Is the code clear and maintainable?
            4. Robustness: Does it include appropriate error handling and validation?
            5. Specification Compliance: Does it match the required function signature and return type?
            
            Synthesis Strategy:
            - Take the core algorithm from the most correct solution
            - Incorporate edge case handling from the most robust solution
            - Adopt efficiency improvements from the most optimized solution
            - Ensure all necessary imports are included
            - Verify function signature matches exactly
            
            Provide ONLY the final function implementation as specified in the output requirements.""",
            contexts_list=solution_attempts
        )

        # Phase 4: Validation and Iterative Refinement
        final_solution = synthesized_solution
        max_retries = 3
        
        for attempt in range(max_retries):
            # Extract test cases from decomposition for validation
            test_cases = await self.generate(
                instruction=f"""Extract test cases from the decomposition analysis:
                Decomposition: {decomposition_summary}
                
                Generate a Python list of test cases as tuples (input, expected_output) that covers:
                - Basic functionality
                - All identified edge cases
                - Boundary conditions
                - Error cases (if applicable)
                
                Format as a JSON-serializable list of tuples.""",
                context=decomposition_summary
            )
            
            try:
                # Validate the solution against test cases
                validation_result = await self.programmer(
                    instruction=f"""Test the provided solution against these test cases:
                    {test_cases}
                    
                    Execute each test case and report any failures with specific error details.
                    If all tests pass, return 'ALL TESTS PASSED'.
                    If any test fails, return detailed failure information including input, expected output, and actual output.""",
                    context=final_solution,
                    max_retries=1
                )
                
                if "ALL TESTS PASSED" in validation_result.upper():
                    break  # Success! Exit the loop
                else:
                    # Revise based on failures
                    final_solution = await self.revise(
                        instruction=f"""Revise the solution to fix the identified failures:
                        Validation Results: {validation_result}
                        Problem Analysis: {decomposition_summary}
                        
                        Specific Requirements:
                        - Address all test failures mentioned in the validation results
                        - Maintain the exact function signature
                        - Ensure proper handling of edge cases
                        - Include all necessary imports
                        - Return the correct data type
                        - Do not introduce new bugs
                        
                        Provide ONLY the revised function implementation as specified in the output requirements.""",
                        context=final_solution
                    )
            except Exception as e:
                # If validation fails unexpectedly, try revision with error info
                final_solution = await self.revise(
                    instruction=f"""Revise the solution to handle potential errors:
                    Error during validation: {str(e)}
                    Problem Analysis: {decomposition_summary}
                    
                    Requirements:
                    - Add defensive programming practices
                    - Include appropriate error handling
                    - Ensure edge cases are covered
                    - Maintain function signature
                    - Include necessary imports
                    
                    Provide ONLY the revised function implementation as specified in the output requirements.""",
                    context=final_solution
                )

        # Phase 5: Final Quality Assurance and Output
        final_output = await self.summarize(
            instruction="""Final quality check:
            - Verify the solution matches the required function signature exactly
            - Ensure all necessary imports are included at the top
            - Confirm return type matches specifications
            - Check that no debugging code or print statements remain
            - Ensure code is clean and follows Python best practices
            
            Return the final solution exactly as it should be output, with no additional text or explanations.
            The output must be ONLY the function implementation as specified in the output requirements.""",
            context=final_solution
        )

        return final_output