# Workflow ID: mbppplus_26_0
# Benchmark: mbppplus
# Data Indices: [68, 20, 19]

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

        # Step 1: Deep problem analysis - extract structure, constraints, edge cases
        problem_analysis = await self.generate(
            instruction="""Perform deep structural analysis of this programming problem:
            1. Identify input/output types and formats (list, string, int, etc.)
            2. Extract explicit and implicit constraints
            3. Infer likely edge cases (empty inputs, single elements, boundaries, invalid formats)
            4. Classify problem type: string manipulation, numeric computation, algorithmic (DP/greedy), data structure operation
            5. Suggest 2-3 potential solution strategies with their trade-offs
            6. Note any potential pitfalls or common mistakes
            Format as structured markdown with clear sections.""",
            context=""
        )

        # Step 2: Parallel strategy generation - 3 different approaches
        strategy_tasks = [
            self.generate(
                instruction=f"""Generate a direct, reference-style solution based on problem analysis:
                Analysis: {problem_analysis}
                
                Requirements:
                - Match exact function signature
                - Prioritize clarity and simplicity
                - Include necessary imports inside function
                - Return correct data type as specified
                - Do NOT include test cases or explanations
                - Code only, no markdown or text""",
                context=problem_analysis
            ),
            self.generate(
                instruction=f"""Generate a robust, defensive solution with comprehensive edge case handling:
                Analysis: {problem_analysis}
                
                Requirements:
                - Handle all inferred edge cases from analysis
                - Include input validation where appropriate
                - Use try/except blocks if potential runtime errors exist
                - Maintain efficiency while being defensive
                - Match exact function signature
                - Code only, no explanations""",
                context=problem_analysis
            ),
            self.generate(
                instruction=f"""Generate an optimized, algorithmically sophisticated solution:
                Analysis: {problem_analysis}
                
                Requirements:
                - Use most efficient algorithm for problem type
                - Consider time/space complexity trade-offs
                - Use appropriate data structures
                - Include comments only if complex logic
                - Match exact function signature
                - Code only, no explanations""",
                context=problem_analysis
            )
        ]
        
        # Execute strategies in parallel
        strategy_solutions = await asyncio.gather(*strategy_tasks)

        # Step 3: Ensemble synthesis - combine best elements from all strategies
        synthesized_solution = await self.ensemble(
            instruction="""Synthesize the best solution by combining elements from all three candidates:
            Evaluation criteria:
            1. Correctness: Must handle all edge cases and constraints
            2. Efficiency: Optimal time/space complexity
            3. Readability: Clean, well-structured code
            4. Robustness: Defensive against invalid inputs
            5. Compliance: Exact function signature and return type
            
            Synthesis strategy:
            - Take core logic from most direct solution
            - Add edge case handling from defensive solution
            - Incorporate optimizations from algorithmic solution
            - Remove redundant or conflicting elements
            - Ensure code is production-ready and passes rigorous testing
            
            Output ONLY the final function implementation, including necessary imports inside the function.""",
            contexts_list=strategy_solutions
        )

        # Step 4: Generate comprehensive test cases (including edge cases)
        test_cases = await self.generate(
            instruction=f"""Generate comprehensive test cases based on problem analysis:
            Analysis: {problem_analysis}
            
            Include:
            - Basic functionality tests
            - Edge cases (empty, single element, boundaries)
            - Invalid input scenarios
            - Performance stress tests if applicable
            - Format as Python assert statements
            - 8-12 diverse test cases covering all scenarios""",
            context=problem_analysis
        )

        # Step 5: Iterative refinement loop (max 2 iterations)
        current_solution = synthesized_solution
        for iteration in range(2):
            # Validate solution against generated test cases
            validation_feedback = await self.generate(
                instruction=f"""Validate this solution against the test cases:
                Solution: {current_solution}
                Test Cases: {test_cases}
                
                Check for:
                1. Syntax errors
                2. Logic errors
                3. Edge case failures
                4. Type mismatches
                5. Performance issues
                
                Provide specific, actionable feedback for improvement.
                If solution passes all tests, respond with 'VALIDATED'.""",
                context=f"Solution: {current_solution}\n\nTest Cases: {test_cases}"
            )
            
            # Early termination if validated
            if "VALIDATED" in validation_feedback.upper():
                break
                
            # Revise solution based on feedback
            current_solution = await self.revise(
                instruction=f"""Revise solution based on validation feedback:
                Feedback: {validation_feedback}
                
                Requirements:
                - Fix all identified issues
                - Maintain function signature
                - Preserve working functionality
                - Improve robustness
                - Output only the revised function implementation""",
                context=current_solution
            )

        # Step 6: Final cleanup - extract only the function implementation
        final_implementation = await self.summarize(
            instruction="""Extract ONLY the final function implementation:
            - Remove all markdown, explanations, or extra text
            - Ensure imports are inside the function if needed
            - Verify exact function signature matches problem
            - Output should be ready to execute as-is
            - No additional text before or after the code""",
            context=current_solution
        )

        return final_implementation