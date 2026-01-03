# Workflow ID: mbppplus_62_0
# Benchmark: mbppplus
# Data Indices: [356, 358, 108]

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

        # PHASE 1: PARALLEL PROBLEM DECOMPOSITION
        # Launch three independent analyses: mathematical core, type contracts, edge cases
        decomposition_tasks = [
            self.generate(
                instruction="""Analyze the mathematical or algorithmic core of this problem.
                - What fundamental operation is being performed? (e.g., bit manipulation, averaging, counting unique values)
                - What is the underlying pattern or formula?
                - Are there known algorithms or mathematical identities that apply?
                - Express the core logic in pseudocode or mathematical notation.
                Be precise and abstract away from specific variable names.""",
                context=""
            ),
            self.generate(
                instruction="""Extract exact type contracts and structural requirements.
                - What are the input parameter types and structures? (list, tuple, int, etc.)
                - What is the exact expected return type and format?
                - Are there constraints on order, mutability, or uniqueness?
                - Must the solution preserve input order or can it use sets/dicts?
                - List every type-related requirement explicitly.""",
                context=""
            ),
            self.generate(
                instruction="""Enumerate all possible edge cases and boundary conditions.
                - What are the minimal valid inputs? (empty list, single element, zero, negative numbers)
                - What are the maximal or extreme inputs? (large numbers, long lists)
                - What malformed or unexpected inputs might occur? (None, wrong types, duplicates)
                - What are the boundary values where behavior might change?
                - For each edge case, specify the expected output or behavior.
                Think defensively and exhaustively.""",
                context=""
            )
        ]
        
        math_analysis, type_analysis, edge_analysis = await asyncio.gather(*decomposition_tasks)

        # PHASE 2: SYNTHESIZE INTO UNIFIED SPECIFICATION
        unified_spec = await self.ensemble(
            instruction="""Synthesize the three analyses into a single comprehensive specification.
            Combine:
            1. The mathematical/algorithmic core from context 1
            2. The type contracts and structural requirements from context 2
            3. The edge cases and boundary conditions from context 3
            
            Produce a unified document that includes:
            - Clear problem restatement in technical terms
            - Pseudocode or step-by-step algorithm
            - Exact input/output type signatures
            - List of edge cases with expected behaviors
            - Any constraints or invariants that must be maintained
            Format this as a structured specification that can directly guide code implementation.""",
            contexts_list=[math_analysis, type_analysis, edge_analysis]
        )

        # PHASE 3: GENERATE INITIAL CODE IMPLEMENTATION
        initial_code = await self.generate(
            instruction=f"""Generate a Python function implementation based on this specification:
            {unified_spec}
            
            Requirements:
            - Use the EXACT function name and parameters from the original problem
            - Include all necessary imports INSIDE the function if needed
            - Return the correct data type as specified
            - Handle all edge cases identified in the specification
            - Write clean, efficient, and readable code
            - Output ONLY the function implementation as raw text (no markdown, no explanations)
            - If imports are needed, place them at the top of the function body""",
            context=unified_spec
        )

        # PHASE 4: GENERATE VALIDATION TEST CASES (SIMULATED)
        test_cases = await self.generate(
            instruction="""Generate a comprehensive set of test cases to validate the solution.
            Include:
            - The example test cases shown in the problem (if any)
            - Additional typical cases covering normal operation
            - Edge cases identified in the specification (empty inputs, zeros, negatives, etc.)
            - Boundary cases and extreme values
            - Type variation cases (if applicable)
            Format each test case as a tuple: (input_args, expected_output)
            Output as a Python list of tuples.""",
            context=unified_spec
        )

        # PHASE 5: VALIDATE AND ITERATIVELY REVISE (MAX 2 ITERATIONS)
        current_code = initial_code
        for iteration in range(2):
            validation_result = await self.generate(
                instruction=f"""Validate this code against the test cases:
                Code:
                {current_code}
                
                Test Cases:
                {test_cases}
                
                Simulate execution for each test case.
                Report:
                1. Which test cases pass
                2. Which test cases fail and why (exact error or mismatch)
                3. Specific lines of code that need modification
                4. Suggestions for fixing the failures while preserving existing functionality
                Be brutally honest and precise. If all pass, say 'ALL TESTS PASS'.""",
                context=f"Code: {current_code}\n\nTest Cases: {test_cases}"
            )
            
            if "ALL TESTS PASS" in validation_result.upper():
                break
                
            # Revise code based on validation feedback
            current_code = await self.revise(
                instruction=f"""Revise the code to fix the failures identified in validation:
                Validation Feedback:
                {validation_result}
                
                Original Specification:
                {unified_spec}
                
                Requirements:
                - Fix only the identified issues
                - Preserve existing correct functionality
                - Maintain type consistency and edge case handling
                - Output ONLY the revised function implementation as raw text
                - Keep imports inside function if needed""",
                context=current_code
            )
        else:
            # If we exhausted iterations, do one final ensemble with original and revised versions
            final_ensemble = await self.ensemble(
                instruction="""Select the best version of the code from these candidates.
                Consider:
                - Correctness on edge cases
                - Type consistency
                - Code clarity and efficiency
                - Adherence to specification
                Choose the most robust implementation even if not perfect.
                Output ONLY the selected function implementation as raw text.""",
                contexts_list=[initial_code, current_code]
            )
            current_code = final_ensemble

        # FINAL SANITIZATION: Ensure output is clean function implementation only
        sanitized_code = await self.revise(
            instruction="""Sanitize this code to meet submission requirements:
            - Must be ONLY the function implementation (no extra text, markdown, or explanations)
            - Must use exact function name and parameters from original problem
            - Must include necessary imports inside function if needed
            - Must return correct data type
            - Remove any debugging prints or extra comments
            - Ensure clean, production-ready code
            Output ONLY the sanitized function as raw text.""",
            context=current_code
        )

        return sanitized_code