# Workflow ID: mbppplus_112_0
# Benchmark: mbppplus
# Data Indices: [173, 213, 71]

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
        import math
        
        # Phase 1: Problem Classification and Requirement Extraction
        classification = await self.generate(
            instruction="""Perform deep problem analysis:
            1. Classify problem type: mathematical, logical, string processing, data structure, or hybrid
            2. Identify expected input/output types and formats
            3. Extract key constraints and edge cases (empty inputs, boundary conditions, special values)
            4. Determine if solution requires exact calculation, pattern matching, comparison, or transformation
            5. Assess whether built-in functions are permitted or if algorithmic implementation is required
            6. Identify potential pitfalls and common mistakes for this problem type
            7. Recommend 2-3 viable solution strategies with their trade-offs
            8. Specify any required imports (re, math, etc.) based on problem needs
            Provide structured, comprehensive analysis.""",
            context=""
        )

        # Phase 2: Parallel Solution Generation
        solution_attempts = await asyncio.gather(
            self.generate(
                instruction=f"""Generate Solution Attempt 1 - Algorithmic Approach:
                Based on problem classification: {classification}
                
                Implement a clean, readable solution focusing on:
                - Explicit step-by-step logic
                - Comprehensive edge case handling
                - Clear variable names and comments
                - Adherence to specified function signature
                - Return type consistency
                
                Include detailed comments explaining the approach and edge case handling.
                Format as complete Python function with necessary imports.""",
                context=classification
            ),
            self.generate(
                instruction=f"""Generate Solution Attempt 2 - Optimized/Concise Approach:
                Based on problem classification: {classification}
                
                Implement an efficient, potentially more concise solution focusing on:
                - Algorithmic efficiency and minimal operations
                - Clever use of Python features (comprehensions, built-ins when appropriate)
                - Handling edge cases with minimal code
                - Performance optimization where applicable
                
                Include brief comments on optimizations and edge case handling.
                Format as complete Python function with necessary imports.""",
                context=classification
            ),
            self.generate(
                instruction=f"""Generate Solution Attempt 3 - Robust/Defensive Approach:
                Based on problem classification: {classification}
                
                Implement a highly robust solution focusing on:
                - Comprehensive input validation and error handling
                - Extensive edge case coverage
                - Defensive programming practices
                - Clear failure modes and graceful degradation
                - Documentation of assumptions and limitations
                
                Include thorough comments on validation logic and edge cases.
                Format as complete Python function with necessary imports.""",
                context=classification
            )
        )

        # Phase 3: Solution Synthesis and Refinement
        synthesized_solution = await self.ensemble(
            instruction="""Synthesize the best elements from all solution attempts:
            1. Evaluate each solution for correctness, robustness, and efficiency
            2. Identify the strongest approach for core logic
            3. Incorporate the best edge case handling from any solution
            4. Ensure code is clean, readable, and follows Python best practices
            5. Verify function signature and return type match requirements
            6. Remove redundant comments while preserving essential explanations
            7. Optimize for both correctness and performance
            8. Ensure all identified edge cases are properly handled
            
            Produce a final, polished solution that represents the optimal combination of all attempts.""",
            contexts_list=solution_attempts
        )

        # Phase 4: Validation and Iterative Refinement
        final_solution = synthesized_solution
        for iteration in range(3):  # Maximum 3 refinement iterations
            validation = await self.generate(
                instruction=f"""Rigorously validate the solution:
                Solution to validate:
                {final_solution}
                
                Based on original problem classification: {classification}
                
                1. Generate 5-7 test cases including edge cases identified in classification
                2. Manually trace through each test case to verify correctness
                3. Check for type consistency, boundary conditions, and error handling
                4. Identify any logical flaws, missing edge cases, or implementation errors
                5. If issues found, provide specific, actionable feedback for correction
                6. If no issues found, confirm solution is correct and robust
                
                Format feedback as: "ISSUES FOUND:" followed by specific corrections needed, 
                or "VALIDATION PASSED:" if solution is correct.""",
                context=final_solution
            )
            
            if "ISSUES FOUND:" in validation:
                final_solution = await self.revise(
                    instruction=f"""Revise solution based on validation feedback:
                    Validation feedback:
                    {validation}
                    
                    Original problem classification:
                    {classification}
                    
                    Specific revision requirements:
                    1. Address all issues identified in validation feedback
                    2. Maintain function signature and return type
                    3. Preserve core logic while fixing identified flaws
                    4. Enhance edge case handling as needed
                    5. Keep code clean and readable
                    6. Add comments explaining fixes if non-trivial
                    
                    Return complete revised solution.""",
                    context=final_solution
                )
            else:
                break  # Validation passed, no more iterations needed

        # Phase 5: Final Polish and Output Preparation
        final_output = await self.revise(
            instruction="""Final polish for submission:
            1. Ensure code follows exact required format (function signature, imports, etc.)
            2. Remove any unnecessary comments or debug statements
            3. Verify all imports are included and properly placed
            4. Ensure return statements match expected types
            5. Format code with proper indentation and spacing
            6. Remove any validation or test code that isn't part of the core solution
            7. Make absolutely certain the solution is self-contained and will execute as-is
            
            Return ONLY the final function implementation with imports, nothing else.""",
            context=final_solution
        )
        
        return final_output