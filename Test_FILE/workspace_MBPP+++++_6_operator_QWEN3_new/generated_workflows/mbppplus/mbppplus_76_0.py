# Workflow ID: mbppplus_76_0
# Benchmark: mbppplus
# Data Indices: [124, 45]

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
        """
        Universal workflow for programming problem-solving domain.
        Uses parallel exploration, synthesis, test-driven implementation, and iterative refinement.
        """
        import asyncio
        import re

        # PHASE 1: PARALLEL PROBLEM EXPLORATION
        # Generate multiple perspectives simultaneously to avoid premature commitment to one approach
        perspectives = await asyncio.gather(
            self.generate(
                instruction="""Analyze this programming problem from a STRING MANIPULATION perspective:
                - What string operations are needed? (splitting, regex, parsing, etc.)
                - What patterns or delimiters are involved?
                - How should edge cases like empty strings or malformed input be handled?
                - What's the expected output format?""",
                context=""
            ),
            self.generate(
                instruction="""Analyze this programming problem from a MATHEMATICAL/ALGORITHMIC perspective:
                - What mathematical operations or formulas are implied?
                - Are there sequences, series, or combinatorial aspects?
                - What boundary conditions or edge cases need consideration?
                - What's the computational complexity of potential solutions?""",
                context=""
            ),
            self.generate(
                instruction="""Analyze this programming problem from a DATA STRUCTURE perspective:
                - What data structures are most appropriate? (lists, sets, dictionaries, etc.)
                - Are there requirements for order preservation, uniqueness, or efficient lookup?
                - How should the input be transformed or processed?
                - What edge cases related to data structure operations should be considered?""",
                context=""
            )
        )

        # PHASE 2: SYNTHESIZE BEST APPROACH
        # Combine the multiple perspectives into a coherent strategy
        synthesized_strategy = await self.ensemble(
            instruction="""Synthesize the multiple analytical perspectives into a unified solution strategy:
            - Identify the dominant approach (string, math, or data structure) based on problem requirements
            - Resolve any conflicts between perspectives
            - Create a step-by-step plan that incorporates the strongest insights from each perspective
            - Explicitly address edge cases mentioned in any perspective
            - Format as clear, actionable steps for implementation""",
            contexts_list=perspectives
        )

        # PHASE 3: GENERATE TEST CASES (INCLUDING EDGE CASES)
        # Anticipate test cases beyond those shown, focusing on robustness
        test_cases = await self.generate(
            instruction=f"""Generate comprehensive test cases for this problem, including edge cases:
            Based on the synthesized strategy: {synthesized_strategy}
            
            Generate at least 5 test cases including:
            - The basic cases shown in examples (if any)
            - Empty input cases
            - Single element/character cases
            - Boundary condition cases
            - Cases with duplicates or repeated patterns
            - Malformed or unexpected input cases
            - Maximum/minimum value cases
            
            Format each test case as: input -> expected_output""",
            context=synthesized_strategy
        )

        # PHASE 4: IMPLEMENT SOLUTION
        # Generate code that must handle the generated test cases
        solution_attempt = await self.programmer(
            instruction=f"""Implement a Python solution for this problem that handles ALL test cases:
            Strategy: {synthesized_strategy}
            
            Test Cases to handle:
            {test_cases}
            
            Requirements:
            - Use the exact function signature specified in the problem
            - Handle all edge cases identified in test cases
            - Return the correct data type (list, tuple, int, etc.)
            - Include necessary imports within the function if needed
            - Write clean, readable code with appropriate variable names
            - Ensure the solution is efficient for the problem constraints""",
            context=f"Strategy: {synthesized_strategy}\n\nTest Cases: {test_cases}"
        )

        # PHASE 5: ITERATIVE REFINEMENT (UP TO 3 ATTEMPTS)
        # Validate and refine the solution if needed
        current_solution = solution_attempt
        for iteration in range(3):
            validation = await self.generate(
                instruction=f"""Critically validate this solution against requirements and test cases:
                Solution: {current_solution}
                
                Check for:
                - Correctness: Does it produce the right output for all test cases?
                - Robustness: Does it handle edge cases properly?
                - Code quality: Is it clean, readable, and efficient?
                - Specification compliance: Does it match the required function signature?
                
                If any issues are found, describe them specifically. If perfect, say "VALIDATED". """,
                context=current_solution
            )
            
            if "VALIDATED" in validation or "validated" in validation:
                break
            else:
                current_solution = await self.revise(
                    instruction=f"""Revise the solution to fix these issues:
                    Validation feedback: {validation}
                    
                    Requirements:
                    - Maintain the exact function signature
                    - Fix all identified issues while preserving correct functionality
                    - Ensure edge cases from test cases are handled
                    - Improve code quality if needed
                    - Return the complete revised implementation""",
                    context=current_solution
                )

        # PHASE 6: FINAL EXTRACTION AND RETURN
        # Extract just the code implementation from the final solution
        final_code = await self.generate(
            instruction="""Extract ONLY the Python function implementation from this text:
            - Remove any explanatory text, markdown, or comments not part of the code
            - Preserve all imports, function signature, and implementation exactly
            - Return ONLY the code, nothing else
            - Ensure the code is ready to be executed as-is""",
            context=current_solution
        )

        return final_code