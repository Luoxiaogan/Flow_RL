# Workflow ID: mbppplus_90_0
# Benchmark: mbppplus
# Data Indices: [313, 348, 333]

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

        # Phase 1: Problem Deconstruction - Extract core patterns and constraints
        deconstruction = await self.generate(
            instruction="""Perform deep problem deconstruction:
            1. Identify the primary data structure involved (string, tuple, number, etc.)
            2. Extract all explicit and implicit constraints
            3. List edge cases (empty inputs, single elements, boundary values)
            4. Determine if the problem is iterative, recursive, mathematical, or combinatorial
            5. Note any type conversion or return type requirements
            6. Identify key operations (comparison, counting, transformation, etc.)
            Present as structured analysis with clear sections.""",
            context=""
        )

        # Phase 2: Strategy Generation - Create multiple solution approaches
        strategy_context = f"Problem Analysis:\n{deconstruction}"
        
        # Generate 3 different solution strategies in parallel
        strategies = await asyncio.gather(
            self.generate(
                instruction=f"""Generate Solution Strategy 1:
                Based on the analysis: {deconstruction}
                
                Create an ITERATIVE solution approach:
                - Use loops and direct traversal
                - Focus on step-by-step processing
                - Handle edge cases explicitly
                - Ensure type consistency in returns
                Format as detailed pseudocode with comments explaining key decisions.""",
                context=strategy_context
            ),
            self.generate(
                instruction=f"""Generate Solution Strategy 2:
                Based on the analysis: {deconstruction}
                
                Create a RECURSIVE or MATHEMATICAL solution approach:
                - Use recursion or mathematical formulas
                - Focus on base cases and recurrence relations
                - Consider memoization if applicable
                - Ensure termination conditions are clear
                Format as detailed pseudocode with comments explaining key decisions.""",
                context=strategy_context
            ),
            self.generate(
                instruction=f"""Generate Solution Strategy 3:
                Based on the analysis: {deconstruction}
                
                Create a FUNCTIONAL or DECLARATIVE solution approach:
                - Use built-in functions, comprehensions, or functional programming
                - Focus on elegance and conciseness
                - Leverage Python's standard library effectively
                - Ensure readability and maintainability
                Format as detailed pseudocode with comments explaining key decisions.""",
                context=strategy_context
            )
        )

        # Phase 3: Solution Synthesis - Combine best elements from all strategies
        synthesized_solution = await self.ensemble(
            instruction="""Synthesize the best solution from all approaches:
            1. Compare all three strategies for correctness, efficiency, and elegance
            2. Select the approach that best handles edge cases identified in deconstruction
            3. Incorporate the strongest elements from each strategy
            4. Ensure the solution matches the exact function signature and return type
            5. Add comprehensive comments explaining key decisions and edge case handling
            6. Format as complete, runnable Python code with the exact function name specified
            
            CRITICAL: The output must be ONLY the function implementation with necessary imports.
            Do NOT include any additional text, explanations, or markdown formatting.
            The code must be ready to execute as-is.""",
            contexts_list=strategies
        )

        # Phase 4: Validation and Refinement - Ensure robustness and correctness
        refined_solution = await self.revise(
            instruction="""Refine the solution with extreme rigor:
            1. Verify that all edge cases from deconstruction are handled
            2. Ensure type consistency (return exactly what's expected - list, tuple, int, etc.)
            3. Check for off-by-one errors, infinite loops, or recursion depth issues
            4. Confirm that empty inputs, single elements, and boundary values are handled correctly
            5. Remove any unnecessary complexity or over-engineering
            6. Ensure variable names are clear and meaningful
            7. Format code according to Python best practices (PEP 8)
            
            CRITICAL: Output ONLY the refined function implementation.
            No additional text, explanations, or formatting allowed.
            The code must be production-ready and pass all test cases including edge cases.""",
            context=synthesized_solution
        )

        # Phase 5: Final Formatting - Ensure exact output format compliance
        final_solution = await self.revise(
            instruction="""Final formatting pass:
            1. Ensure the function name matches EXACTLY what's specified in the problem
            2. Verify parameter names are correct
            3. Include ONLY necessary imports at the top of the function
            4. Return the appropriate data type as shown in test cases
            5. Remove any debug statements, print calls, or unnecessary comments
            6. Ensure the code is clean, minimal, and focused
            
            OUTPUT REQUIREMENTS:
            - Generate ONLY the function implementation
            - Use the EXACT function name from the reference code
            - Include all necessary imports at the top
            - Preserve function signatures including parameter names
            - Do NOT wrap in any outer function or class
            - Return appropriate data types as shown in tests
            
            The output must be ready for immediate execution and testing.""",
            context=refined_solution
        )

        return final_solution