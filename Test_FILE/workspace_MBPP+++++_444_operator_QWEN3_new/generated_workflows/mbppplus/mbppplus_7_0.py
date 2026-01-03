# Workflow ID: mbppplus_7_0
# Benchmark: mbppplus
# Data Indices: [95, 6, 320]

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
        """
        Universal workflow for programming problem solving with architectural sophistication.
        Features: Parallel solution generation, ensemble synthesis, validation-triggered refinement.
        """
        import asyncio
        import re

        # Phase 1: Comprehensive Problem Analysis
        analysis = await self.generate(
            instruction="""Perform deep analysis of this programming problem:
            1. Extract exact function signature (name, parameters, return type)
            2. Identify input/output data types and structures
            3. Determine edge cases (empty inputs, single elements, boundary conditions)
            4. Note any required Python modules (re, math, etc.)
            5. Identify potential pitfalls and common mistakes
            6. Extract any examples or test cases provided
            7. Determine if order preservation is required
            8. Note any performance or efficiency considerations
            9. Identify domain-specific knowledge required
            Present analysis in structured format with clear sections.""",
            context=""
        )

        # Phase 2: Parallel Solution Generation
        solution_approaches = await asyncio.gather(
            self.generate(
                instruction=f"""Generate DIRECT implementation based on problem description:
                - Use exact function signature from analysis
                - Focus on clarity and readability
                - Handle obvious edge cases
                - Include necessary imports at top
                - Return correct data types
                - Follow Python best practices
                Problem Analysis: {analysis}""",
                context=analysis
            ),
            self.generate(
                instruction=f"""Generate REFERENCE-INSPIRED implementation:
                - Study any reference solution patterns in problem
                - Adapt approach to current problem requirements
                - Focus on efficiency and elegance
                - Consider alternative algorithms or data structures
                - Handle edge cases systematically
                - Include necessary imports
                Problem Analysis: {analysis}""",
                context=analysis
            ),
            self.generate(
                instruction=f"""Generate EDGE-CASE FOCUSED implementation:
                - Prioritize robustness over elegance
                - Explicitly handle all edge cases identified in analysis
                - Add defensive programming checks
                - Consider input validation
                - Handle unexpected inputs gracefully
                - Include comprehensive error handling
                - Include necessary imports
                Problem Analysis: {analysis}""",
                context=analysis
            )
        )

        # Phase 3: Ensemble Synthesis
        synthesized_solution = await self.ensemble(
            instruction="""Synthesize the three solution approaches into one optimal solution:
            1. Combine clarity of direct approach with efficiency of reference-inspired approach
            2. Incorporate robustness features from edge-case focused approach
            3. Ensure exact function signature compliance
            4. Verify correct handling of all identified edge cases
            5. Optimize for both correctness and readability
            6. Include only necessary imports
            7. Ensure return types match requirements exactly
            8. Remove any redundant or defensive code that's not needed
            9. Format code according to Python best practices
            10. Present ONLY the final function implementation as required""",
            contexts_list=solution_approaches
        )

        # Phase 4: Validation and Refinement Loop
        max_iterations = 3
        current_solution = synthesized_solution
        
        for iteration in range(max_iterations):
            validation = await self.generate(
                instruction=f"""Validate this solution against problem requirements:
                1. Test against provided examples (if any)
                2. Generate 5-7 additional test cases including edge cases
                3. Verify correct data types (list vs tuple vs set)
                4. Check empty input handling
                5. Verify order preservation when required
                6. Test boundary conditions
                7. Check for off-by-one errors
                8. Verify import statements are correct and minimal
                9. Ensure function signature matches exactly
                10. Identify any remaining bugs or issues
                
                Problem Analysis: {analysis}
                Current Solution: {current_solution}
                
                Return validation results in format:
                VALIDATION_PASSED: [yes/no]
                ISSUES_FOUND: [list of specific issues]
                SUGGESTED_FIXES: [specific fixes for each issue]""",
                context=current_solution
            )

            # Check if validation passed
            if "VALIDATION_PASSED: yes" in validation or "VALIDATION_PASSED: Yes" in validation:
                break
            
            # If validation failed, revise solution
            current_solution = await self.revise(
                instruction=f"""Revise solution to fix identified issues:
                1. Address ALL issues found in validation
                2. Maintain correct function signature
                3. Preserve working parts of solution
                4. Focus fixes on specific problems identified
                5. Do not introduce new issues
                6. Keep code clean and readable
                7. Include only necessary imports
                8. Return ONLY the function implementation
                
                Validation Results: {validation}
                Current Solution: {current_solution}""",
                context=current_solution
            )

        # Final output - ensure it meets exact format requirements
        final_output = await self.revise(
            instruction="""Final cleanup and format verification:
            1. Ensure output contains ONLY the function implementation
            2. Verify exact function name and signature
            3. Include necessary imports at top (inside function if required)
            4. Remove any explanatory text, comments, or markdown
            5. Ensure proper Python syntax and indentation
            6. Return code ready for direct execution
            7. Do NOT wrap in any outer function or class
            8. Match exact return type requirements from problem""",
            context=current_solution
        )

        return final_output