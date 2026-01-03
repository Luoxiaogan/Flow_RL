# Workflow ID: mbppplus_111_0
# Benchmark: mbppplus
# Data Indices: [57, 5]

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
        import json

        # Step 1: Extract core requirements and anticipate edge cases
        requirement_analysis = await self.generate(
            instruction="""Thoroughly analyze the function signature and problem description to extract:
            1. Exact input parameters and their expected types
            2. Expected return type and format
            3. Core functionality required
            4. Potential edge cases (empty inputs, single elements, boundary values, type mismatches)
            5. Any implicit constraints or assumptions
            6. Performance or efficiency considerations
            Present this as a structured JSON-like analysis with clear sections.""",
            context=""
        )

        # Step 2: Generate synthetic test cases for validation
        synthetic_tests = await self.generate(
            instruction=f"""Based on the requirement analysis:
            {requirement_analysis}
            
            Generate 5-7 comprehensive synthetic test cases that cover:
            - Normal cases
            - Edge cases (empty, single element, extreme values)
            - Error cases (if applicable)
            - Type boundary cases
            Format each test case as: input -> expected_output
            Include at least one complex case that tests the core logic thoroughly.""",
            context=requirement_analysis
        )

        # Step 3: Parallel generation of multiple implementation strategies
        strategy_instructions = [
            """Implement using built-in Python libraries and functions (e.g., collections.Counter, max with key, etc.). 
            Focus on readability and Pythonic style. Include comprehensive error handling for edge cases identified.""",
            
            """Implement using manual iteration and dictionary counting. Focus on explicit logic that's easy to trace and debug. 
            Include detailed comments explaining each step. Handle all edge cases explicitly.""",
            
            """Implement using sorting or grouping techniques. Focus on algorithmic efficiency and minimal memory usage. 
            Consider time complexity and optimize for large inputs. Include performance comments."""
        ]

        strategy_attempts = await asyncio.gather(
            *[self.generate(
                instruction=f"""{instr}
                
                Requirements context:
                {requirement_analysis}
                
                Validate your implementation against these synthetic tests:
                {synthetic_tests}
                
                Return ONLY the function implementation with necessary imports. 
                Ensure perfect type consistency and edge case handling.
                Include no additional text or explanations.""",
                context=""
            ) for instr in strategy_instructions]
        )

        # Step 4: Execute and validate each strategy
        execution_results = []
        for i, code_attempt in enumerate(strategy_attempts):
            try:
                result = await self.programmer(
                    instruction=f"""Execute and validate this implementation against the synthetic tests.
                    Requirements: {requirement_analysis}
                    Tests: {synthetic_tests}
                    If any test fails, return the error. Otherwise, return 'PASSED'.""",
                    context=code_attempt,
                    max_retries=2
                )
                execution_results.append({
                    'code': code_attempt,
                    'result': result,
                    'strategy_index': i
                })
            except Exception as e:
                execution_results.append({
                    'code': code_attempt,
                    'result': f"EXECUTION_ERROR: {str(e)}",
                    'strategy_index': i
                })

        # Step 5: Ensemble - select the best implementation
        successful_implementations = [item['code'] for item in execution_results if 'PASSED' in item['result']]
        
        if successful_implementations:
            if len(successful_implementations) == 1:
                selected_code = successful_implementations[0]
            else:
                selected_code = await self.ensemble(
                    instruction="""Select the best implementation based on:
                    1. Correctness (all must be correct, but prefer most robust)
                    2. Readability and maintainability
                    3. Efficiency and performance
                    4. Comprehensive edge case handling
                    5. Clean, well-commented code
                    Return ONLY the selected implementation code.""",
                    contexts_list=successful_implementations
                )
        else:
            # Fallback: take the first attempt and try to revise
            selected_code = execution_results[0]['code'] if execution_results else ""

        # Step 6: Final revision for polish and robustness
        final_code = await self.revise(
            instruction=f"""Polish this code implementation:
            {selected_code}
            
            Based on requirements:
            {requirement_analysis}
            
            Ensure:
            1. Perfect type consistency (return type matches expectations)
            2. All edge cases are handled gracefully
            3. Code is clean, well-commented, and follows Python best practices
            4. No unnecessary imports or complexity
            5. Function signature matches exactly what was specified
            Return ONLY the final implementation with necessary imports.""",
            context=selected_code
        )

        return final_code