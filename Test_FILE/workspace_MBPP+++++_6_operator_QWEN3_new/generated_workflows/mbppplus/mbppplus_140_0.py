# Workflow ID: mbppplus_140_0
# Benchmark: mbppplus
# Data Indices: [7, 184]

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

        # Phase 1: Problem Decomposition & Strategy Planning
        decomposition = await self.decompose(
            instruction="""Break down this programming problem into fundamental components:
            1. INPUT ANALYSIS: What data types and structures are we working with? (strings, numbers, lists, tuples, etc.)
            2. OUTPUT SPECIFICATION: What should the function return? (exact type, format, constraints)
            3. CORE ALGORITHM: What computational approach is needed? (mathematical, string parsing, data structure manipulation, etc.)
            4. EDGE CASES: What boundary conditions must be handled? (empty inputs, single elements, extreme values, type variations)
            5. CONSTRAINTS: Any performance, memory, or implementation restrictions?
            6. TEST CASES: What examples are provided and what do they reveal about requirements?
            Return structured subproblems with clear dependencies.""",
            context=""
        )

        # Phase 2: Parallel Strategy Exploration
        # Generate three different solution approaches concurrently
        strategy_tasks = [
            self.generate(
                instruction=f"""Develop a direct implementation solution based on problem decomposition:
                Decomposition: {json.dumps(decomposition)}
                
                Approach: Solve from first principles without reference to any provided solution.
                - Focus on clean, readable code
                - Handle all identified edge cases
                - Match exact function signature and return types
                - Include necessary imports within function if needed
                - Write defensive code that gracefully handles unexpected inputs""",
                context=""
            ),
            self.generate(
                instruction=f"""Develop a reference-inspired solution:
                Decomposition: {json.dumps(decomposition)}
                
                Approach: Study the reference solution pattern (if available) but implement your own version.
                - Understand the algorithmic approach used in reference
                - Reimplement with your own variable names and structure
                - Improve upon reference if possible (better edge case handling, efficiency)
                - Maintain exact function signature and return types
                - Never copy code directly - only the conceptual approach""",
                context=""
            ),
            self.generate(
                instruction=f"""Develop a test-case-driven solution:
                Decomposition: {json.dumps(decomposition)}
                
                Approach: Reverse-engineer requirements from test cases and problem description.
                - Analyze provided test cases to infer behavior
                - Design solution that passes all shown tests
                - Extrapolate to handle likely edge cases not shown
                - Focus on robustness and type safety
                - Ensure output matches exact format in tests""",
                context=""
            )
        ]
        
        strategy_results = await asyncio.gather(*strategy_tasks)

        # Phase 3: Solution Synthesis & Ensemble
        synthesized_solution = await self.ensemble(
            instruction="""Synthesize the best elements from all three solution approaches:
            1. Evaluate each solution for:
               - Correctness (handles core functionality)
               - Completeness (covers edge cases)
               - Efficiency (algorithmic complexity)
               - Code quality (readability, structure)
               - Compliance (matches required signature and types)
            2. Combine strengths:
               - Take the most robust algorithmic approach
               - Incorporate the best edge case handling
               - Use the cleanest code structure
               - Ensure type safety and format compliance
            3. Resolve conflicts by prioritizing:
               - Correctness over elegance
               - Completeness over brevity
               - Robustness over performance (unless specified otherwise)
            4. Output only the final function implementation with exact required format.""",
            contexts_list=strategy_results
        )

        # Phase 4: Iterative Refinement & Validation
        current_solution = synthesized_solution
        for iteration in range(3):  # Maximum 3 refinement iterations
            # Generate edge case tests based on decomposition
            edge_case_tests = await self.generate(
                instruction=f"""Generate comprehensive test cases based on problem decomposition:
                Decomposition: {json.dumps(decomposition)}
                Current Solution: {current_solution}
                
                Create 5-10 edge case tests including:
                - Empty inputs
                - Single element cases
                - Boundary values
                - Type variations
                - Unexpected but plausible inputs
                Format as Python assert statements.""",
                context=current_solution
            )

            # Validate solution against edge cases
            validation = await self.programmer(
                instruction=f"""Test the current solution against generated edge cases:
                Solution: {current_solution}
                Edge Cases: {edge_case_tests}
                
                Execute these tests and identify any failures.
                If all tests pass, return 'ALL TESTS PASSED'.
                If any fail, explain exactly what failed and why.""",
                context=current_solution
            )

            # Break if all tests pass
            if "ALL TESTS PASSED" in validation.upper():
                break

            # Revise solution based on failures
            current_solution = await self.revise(
                instruction=f"""Revise the solution to fix identified issues:
                Current Solution: {current_solution}
                Validation Results: {validation}
                Decomposition: {json.dumps(decomposition)}
                
                Specific revision requirements:
                1. Fix all identified failures
                2. Maintain existing functionality that works
                3. Improve robustness for similar edge cases
                4. Keep code clean and readable
                5. Preserve exact function signature and return types
                6. Add defensive checks where appropriate
                
                Output only the revised function implementation.""",
                context=current_solution
            )

        # Phase 5: Final Formatting & Compliance Check
        final_solution = await self.generate(
            instruction=f"""Ensure final solution meets all format requirements:
            Current Solution: {current_solution}
            Problem Requirements: {self.problem_text}
            
            Format strictly according to these rules:
            1. Output ONLY the function implementation (no explanations)
            2. Use EXACT function name from problem
            3. Include all necessary imports at top of function
            4. Preserve exact parameter names and order
            5. Return appropriate data types as shown in tests
            6. No outer functions, classes, or wrappers
            7. Code must be syntactically valid Python
            
            If any adjustments needed, make them now. Output only the formatted code.""",
            context=current_solution
        )

        return final_solution