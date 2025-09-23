# Workflow ID: mbppplus_27_0
# Benchmark: mbppplus
# Data Indices: [172, 222]

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

        # Step 1: Classify the problem type and extract key constraints
        classification = await self.generate(
            instruction="""Analyze the programming problem and classify it:
            1. What category does it belong to? (e.g., string manipulation, mathematical computation, list/set operations, pattern matching)
            2. What are the explicit input/output types and formats?
            3. What edge cases must be handled? (e.g., empty inputs, single elements, duplicates, boundary conditions)
            4. Are there any ambiguities in the problem statement that need resolution?
            5. What are the performance or efficiency constraints (if any)?
            Provide a structured JSON response with keys: category, input_format, output_format, edge_cases, ambiguities, constraints.""",
            context=""
        )

        # Step 2: Decompose the problem into subproblems based on classification
        decomposition = await self.decompose(
            instruction=f"""Break down this {classification} problem into atomic, solvable subproblems.
            Each subproblem should be independently addressable and have clear input/output.
            Consider dependencies between subproblems (e.g., 'extract pattern' must precede 'search for pattern').
            Return as a list of subproblem dictionaries with 'id', 'description', and 'dependencies'.""",
            context=classification
        )

        # Step 3: Generate multiple solution strategies in parallel
        solution_strategies = [
            "Implement using built-in Python methods and standard library functions",
            "Implement using manual iteration and index tracking for maximum control",
            "Implement using regular expressions for pattern matching (if applicable)",
            "Implement using functional programming constructs (map, filter, reduce)"
        ]

        strategy_attempts = await asyncio.gather(*[
            self.generate(
                instruction=f"""Generate a complete Python function implementation for this problem using the following strategy:
                Strategy: {strategy}
                Problem Classification: {classification}
                Subproblems: {json.dumps(decomposition)}
                
                Requirements:
                - Handle all edge cases identified in classification
                - Match exact function signature and return type
                - Include necessary imports
                - Be robust against invalid inputs
                - Prioritize clarity and correctness over premature optimization
                
                Return ONLY the function implementation as a raw Python code block.""",
                context=""
            ) for strategy in solution_strategies
        ])

        # Step 4: Generate comprehensive test cases including edge cases
        test_cases = await self.generate(
            instruction=f"""Generate a comprehensive set of test cases for this problem, including:
            - All examples provided in the original problem
            - Edge cases identified in classification: {classification}
            - Boundary conditions (empty strings, single characters, maximum lengths, etc.)
            - Invalid input scenarios (if applicable)
            - Performance stress tests (if applicable)
            
            Format as a Python list of tuples: (input_args, expected_output)
            Ensure test cases cover all subproblems identified in decomposition: {json.dumps(decomposition)}""",
            context=classification
        )

        # Step 5: Validate each solution against test cases in parallel
        validation_results = []
        for i, solution in enumerate(strategy_attempts):
            try:
                validation = await self.programmer(
                    instruction=f"""Execute the following test cases on the provided solution:
                    Solution:
                    {solution}
                    
                    Test Cases:
                    {test_cases}
                    
                    Return a JSON object with:
                    - "passed": boolean indicating if all tests passed
                    - "failed_cases": list of failed test cases with expected vs actual output
                    - "error": any execution errors encountered""",
                    context=solution,
                    max_retries=1
                )
                validation_results.append(validation)
            except Exception as e:
                validation_results.append(json.dumps({
                    "passed": False,
                    "failed_cases": [],
                    "error": str(e)
                }))

        # Step 6: Ensemble - select the best solution based on test results
        best_solution = await self.ensemble(
            instruction="""Select the best solution from the candidates based on:
            1. Correctness (all tests passed)
            2. Simplicity and readability
            3. Robustness (handles edge cases gracefully)
            4. Efficiency (appropriate for problem constraints)
            5. Adherence to specified output format
            
            If multiple solutions pass all tests, prefer the most readable and maintainable.
            If no solution passes all tests, select the one with the fewest failures and highest partial correctness.
            
            Return ONLY the raw Python code of the selected solution.""",
            contexts_list=strategy_attempts
        )

        # Step 7: Final revision for output format and type consistency
        final_solution = await self.revise(
            instruction=f"""Revise the selected solution to ensure:
            1. Exact function signature matches original problem
            2. Return type is precisely as specified (tuple vs list vs set)
            3. All edge cases from classification are explicitly handled
            4. Code is clean, well-commented, and follows Python best practices
            5. No unnecessary imports or code
            
            Original Classification: {classification}
            Return ONLY the revised Python function implementation.""",
            context=best_solution
        )

        return final_solution