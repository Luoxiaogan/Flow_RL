# Workflow ID: mbppplus_173_0
# Benchmark: mbppplus
# Data Indices: [291, 165]

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

        # Phase 1: Problem Understanding and Specification Extraction
        problem_spec = await self.generate(
            instruction="""Analyze the programming problem with extreme precision. Extract and structure the following:
            1. INPUT SPECIFICATION: What data type is expected? (string, list, tuple, etc.) Any constraints?
            2. OUTPUT SPECIFICATION: What should be returned? Exact data type and format.
            3. TRANSFORMATION RULES: What operation must be performed? Be explicit about edge cases (empty inputs, single elements, duplicates, etc.)
            4. IMPLICIT REQUIREMENTS: Does order matter? Should duplicates be preserved? Any performance constraints?
            5. EXAMPLE VALIDATION: Based on any provided examples, what patterns must the solution follow?
            Format your response as a structured JSON-like outline with clear section headers.""",
            context=""
        )

        # Phase 2: Parallel Strategy Generation
        strategy_tasks = [
            self.generate(
                instruction=f"""Propose a solution strategy using BUILT-IN PYTHON FUNCTIONS and SIMPLE OPERATIONS.
                Problem Context: {problem_spec}
                Focus on: readability, using core Python features (like string methods, list slicing, etc.), and handling edge cases explicitly.
                Avoid external libraries unless absolutely necessary. Provide pseudocode or high-level steps.""",
                context=""
            ),
            self.generate(
                instruction=f"""Propose a solution strategy using ALGORITHMIC LOOPS and MANUAL PROCESSING.
                Problem Context: {problem_spec}
                Focus on: explicit iteration, index management, and step-by-step transformation. Show how you'd handle edge cases manually.
                Provide clear loop structures and variable tracking logic.""",
                context=""
            ),
            self.generate(
                instruction=f"""Propose a solution strategy using ADVANCED LIBRARIES or FUNCTIONAL APPROACHES (regex, itertools, functools, etc.).
                Problem Context: {problem_spec}
                Focus on: leveraging powerful libraries for concise solutions. Justify library choice and show how edge cases are handled.
                Provide import statements and functional patterns.""",
                context=""
            )
        ]
        
        strategy_results = await asyncio.gather(*strategy_tasks)

        # Phase 3: Strategy Synthesis
        synthesized_strategy = await self.ensemble(
            instruction="""Synthesize the three proposed strategies into one optimal approach. Consider:
            - Which approach is most readable and maintainable?
            - Which handles edge cases most robustly?
            - Which is most efficient for typical and extreme inputs?
            - Can you combine strengths from multiple approaches?
            Provide a unified, step-by-step solution plan with explicit handling of edge cases and data type requirements.
            Format as numbered steps with clear rationale for each decision.""",
            contexts_list=strategy_results
        )

        # Phase 4: Code Generation with Context-Aware Instructions
        initial_code = await self.programmer(
            instruction=f"""Generate a complete, production-ready Python function based EXACTLY on this strategy:
            {synthesized_strategy}
            
            CRITICAL REQUIREMENTS:
            - Use the EXACT function name and signature specified in the original problem
            - Handle ALL edge cases mentioned in the problem specification
            - Return the EXACT data type required (list vs tuple vs string, etc.)
            - Include necessary imports at the top of the function
            - Write defensive code that gracefully handles unexpected inputs
            - Prioritize clarity over cleverness - code should be easily understandable
            - Include brief inline comments for complex logic steps""",
            context=synthesized_strategy
        )

        # Phase 5: Generate Validation Test Cases
        test_cases = await self.generate(
            instruction=f"""Generate comprehensive test cases for this solution, including:
            1. BASIC CASES: From the problem examples (if any)
            2. EDGE CASES: Empty inputs, single elements, maximum/minimum values, duplicates
            3. ERROR CASES: Invalid input types, None values, extreme sizes
            4. PERFORMANCE CASES: Large inputs, repeated operations
            Format as Python assert statements that should pass if the solution is correct.
            Include at least 8 test cases covering all scenarios.""",
            context=initial_code
        )

        # Phase 6: Validation and Revision Loop
        current_code = initial_code
        for attempt in range(3):  # Max 3 revision attempts
            validation_result = await self.generate(
                instruction=f"""Validate this code against the following test cases:
                {test_cases}
                
                Execute these tests mentally and identify:
                - Which tests pass and which fail?
                - What is the root cause of any failures?
                - Are there edge cases not covered by these tests?
                Provide specific, actionable feedback for fixing any issues.
                If all tests pass, respond with 'VALIDATION PASSED'.""",
                context=current_code
            )
            
            if "VALIDATION PASSED" in validation_result.upper():
                break
                
            # Revise code based on validation feedback
            current_code = await self.revise(
                instruction=f"""Revise the code to fix all issues identified in validation:
                Validation Feedback: {validation_result}
                
                Specific Requirements:
                - Maintain the exact function signature
                - Fix all identified bugs while preserving correct functionality
                - Add any missing edge case handling
                - Keep code clean and well-commented
                - Ensure return type matches specification exactly""",
                context=current_code
            )
        else:
            # If we exhausted revision attempts, try decomposition as fallback
            decomposition_plan = await self.decompose(
                instruction=f"""Break down this programming problem into atomic subproblems:
                Current Code (with issues): {current_code}
                Validation Failures: {validation_result}
                
                Create subproblems that isolate each failure point. Each subproblem should be independently solvable.
                Focus on: input validation, edge case handling, core transformation logic, and output formatting.""",
                context=current_code
            )
            
            # Solve each subproblem independently
            subproblem_solutions = []
            for subproblem in decomposition_plan:
                sub_solution = await self.programmer(
                    instruction=f"""Solve this specific subproblem:
                    {subproblem['description']}
                    
                    Integrate with overall solution context:
                    {current_code}
                    
                    Return only the code snippet that solves this subproblem.""",
                    context=current_code
                )
                subproblem_solutions.append(sub_solution)
            
            # Reassemble solution
            final_assembly = await self.ensemble(
                instruction=f"""Integrate these subproblem solutions into a complete, working function:
                Subproblem Solutions: {json.dumps(subproblem_solutions)}
                Original Function Structure: {current_code}
                
                Ensure seamless integration, proper variable scoping, and consistent return types.
                Handle any conflicts between subproblem solutions.
                Return the complete, corrected function implementation.""",
                contexts_list=subproblem_solutions
            )
            current_code = final_assembly

        # Final cleanup and standardization
        final_code = await self.revise(
            instruction="""Finalize the code with these requirements:
            1. Ensure EXACT function name and signature as specified in original problem
            2. All necessary imports included at top
            3. No wrapper functions or classes - only the requested function
            4. Clean, professional formatting with consistent indentation
            5. Remove any debug prints or unnecessary comments
            6. Verify return type matches specification exactly
            7. Code should be ready for immediate execution and testing""",
            context=current_code
        )

        return final_code