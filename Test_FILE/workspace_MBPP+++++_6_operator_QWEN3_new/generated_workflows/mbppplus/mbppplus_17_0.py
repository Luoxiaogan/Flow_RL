# Workflow ID: mbppplus_17_0
# Benchmark: mbppplus
# Data Indices: [84, 11]

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

        # Phase 1: Parallel problem analysis from multiple perspectives
        analysis_tasks = [
            self.generate(
                instruction="""Analyze the mathematical/logical structure of this problem:
                - Identify the core algorithmic pattern (e.g., filtering, transformation, reduction, traversal)
                - Determine computational complexity requirements
                - Note any mathematical properties or invariants
                - Suggest optimal data structures for implementation
                Provide detailed technical analysis.""",
                context=""
            ),
            self.generate(
                instruction="""Analyze the data type contracts and edge cases:
                - Specify exact input/output types (list, tuple, set, etc.)
                - Identify all boundary conditions (empty inputs, single elements, max values)
                - List potential type conversion pitfalls
                - Note any order preservation requirements
                Provide comprehensive edge case analysis.""",
                context=""
            ),
            self.generate(
                instruction="""Extract implementation constraints and requirements:
                - Identify any explicit/implicit performance constraints
                - Note language-specific considerations (Python quirks, built-in functions)
                - List forbidden operations or restricted approaches
                - Specify output format requirements (exact return type, structure)
                Provide precise implementation constraints.""",
                context=""
            )
        ]
        
        # Execute analyses in parallel
        analysis_results = await asyncio.gather(*analysis_tasks)
        
        # Phase 2: Synthesize analyses into unified implementation spec
        implementation_spec = await self.ensemble(
            instruction="""Synthesize these three analyses into a single implementation specification:
            1. Mathematical/Algorithmic Analysis: {}
            2. Data Type/Edge Case Analysis: {}
            3. Implementation Constraints: {}
            
            Create a comprehensive implementation plan including:
            - Exact function signature with parameter types and return type
            - Step-by-step pseudocode algorithm
            - Complete list of edge cases to handle
            - Efficiency requirements and complexity targets
            - Any Python-specific implementation notes
            Format as a structured technical specification.""".format(
                analysis_results[0], analysis_results[1], analysis_results[2]
            ),
            contexts_list=analysis_results
        )

        # Phase 3: Generate initial implementation
        initial_code = await self.programmer(
            instruction=f"""Implement the solution based on this specification:
            {implementation_spec}
            
            Requirements:
            - Use the exact function name from the problem
            - Handle all identified edge cases
            - Match specified return types exactly
            - Include necessary imports within the function if needed
            - Write clean, efficient, Pythonic code
            - Do not include test cases or print statements""",
            context=implementation_spec,
            max_retries=1
        )

        # Phase 4: Generate synthetic test cases
        test_cases = await self.generate(
            instruction=f"""Generate comprehensive test cases based on the problem and implementation spec:
            {implementation_spec}
            
            Create 5 test cases including:
            1. Typical case (normal input)
            2. Empty input case
            3. Single element/boundary case
            4. Maximum/minimum value case
            5. Malformed/edge case input
            
            Format as Python assert statements that can be executed directly.
            Include both input and expected output.
            Focus on edge cases identified in the analysis.""",
            context=implementation_spec
        )

        # Phase 5: Validation loop with up to 3 refinement iterations
        current_code = initial_code
        for iteration in range(3):
            # Test the current implementation
            test_result = await self.programmer(
                instruction=f"""Execute these test cases against the implementation:
                Implementation:
                {current_code}
                
                Test Cases:
                {test_cases}
                
                Run all tests and report any failures. If all pass, return 'ALL TESTS PASSED'.
                If any fail, show the failing test and error message.""",
                context=f"{current_code}\n\n{test_cases}",
                max_retries=1
            )
            
            # Check if all tests passed
            if "ALL TESTS PASSED" in test_result.upper():
                break
                
            # If tests failed, revise the implementation
            current_code = await self.revise(
                instruction=f"""Fix the implementation to pass all test cases:
                Current Implementation:
                {current_code}
                
                Test Results:
                {test_result}
                
                Failure Analysis:
                - Identify the root cause of each failure
                - Modify only what's necessary to fix failures
                - Preserve existing correct functionality
                - Maintain all edge case handling
                - Keep code clean and efficient
                Return the complete revised implementation.""",
                context=current_code
            )
        else:
            # If we exhausted all iterations, use the last version
            pass

        # Extract just the function code from the final result
        # Look for the function definition and return only that
        code_lines = current_code.split('\n')
        function_code = []
        in_function = False
        
        for line in code_lines:
            if line.strip().startswith('def ') and not line.strip().startswith('def test_'):
                in_function = True
                function_code = [line]
            elif in_function:
                if line.strip() == '' or (line.startswith(' ') or line.startswith('\t')):
                    function_code.append(line)
                else:
                    break
        
        if not function_code:
            function_code = code_lines  # Fallback if no function found
            
        return '\n'.join(function_code)