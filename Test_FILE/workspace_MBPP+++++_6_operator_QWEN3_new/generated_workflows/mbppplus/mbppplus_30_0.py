# Workflow ID: mbppplus_30_0
# Benchmark: mbppplus
# Data Indices: [152, 171]

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
        from typing import List, Dict, Any

        # Phase 1: Comprehensive Problem Analysis
        problem_analysis = await self.generate(
            instruction="""Perform deep problem analysis with these components:
            1. Problem Classification: Is this primarily about lists/tuples, strings, mathematical operations, or data structures?
            2. Required Operations: What transformations, filters, or computations are needed?
            3. Edge Case Assessment: What edge cases are likely (empty inputs, single elements, duplicates, boundary values)?
            4. Complexity Rating: Simple (single-step), Moderate (2-3 steps), or Complex (requires decomposition)?
            5. Expected Output Format: What data type should be returned (list, tuple, string, etc.)?
            6. Key Constraints: Any specific limitations or requirements mentioned?
            7. Test Case Extraction: Identify any explicit test cases or examples provided.
            Format your response as a structured JSON-like analysis.""",
            context=""
        )

        # Summarize analysis into concise specification
        problem_spec = await self.summarize(
            instruction="""Condense the problem analysis into a concise specification containing:
            - Problem type (categorical)
            - Required operations (bulleted list)
            - Critical edge cases (comma-separated)
            - Complexity level (simple/moderate/complex)
            - Expected return type
            Format as clear, structured text.""",
            context=problem_analysis
        )

        # Phase 2: Adaptive Strategy Selection
        complexity_level = "simple"
        if "complex" in problem_analysis.lower() or "moderate" in problem_analysis.lower():
            complexity_level = "complex"

        if complexity_level == "complex":
            # Decompose complex problems
            subproblems = await self.decompose(
                instruction="""Break this problem into minimal, executable subproblems.
                Each subproblem should be independently solvable and have clear inputs/outputs.
                Specify dependencies between subproblems.
                Focus on creating a logical execution order.""",
                context=problem_spec
            )
            
            # Generate solutions for each subproblem in parallel
            subproblem_solutions = []
            for subproblem in subproblems:
                solution = await self.generate(
                    instruction=f"""Solve this subproblem:
                    {subproblem['description']}
                    
                    Consider dependencies: {subproblem.get('dependencies', 'none')}
                    Follow the overall problem specification: {problem_spec}
                    Return only the solution code/function for this subproblem.""",
                    context=problem_spec
                )
                subproblem_solutions.append(solution)
            
            # Synthesize subproblem solutions
            synthesized_solution = await self.ensemble(
                instruction="""Synthesize these subproblem solutions into a complete, integrated solution.
                Ensure proper data flow between subproblems.
                Handle any interface mismatches.
                Return a single, cohesive code implementation.""",
                contexts_list=subproblem_solutions
            )
            candidate_solution = synthesized_solution
        else:
            # Generate multiple solution approaches in parallel for simple problems
            solution_approaches = await asyncio.gather(
                self.generate(
                    instruction=f"""Generate a solution focusing on algorithmic efficiency:
                    Problem specification: {problem_spec}
                    Optimize for time/space complexity.
                    Use appropriate data structures.
                    Include comprehensive edge case handling.""",
                    context=problem_spec
                ),
                self.generate(
                    instruction=f"""Generate a solution focusing on code readability and maintainability:
                    Problem specification: {problem_spec}
                    Use clear variable names and comments.
                    Structure code for easy understanding.
                    Include edge case handling with explicit checks.""",
                    context=problem_spec
                ),
                self.generate(
                    instruction=f"""Generate a solution focusing on robustness and edge cases:
                    Problem specification: {problem_spec}
                    Handle all identified edge cases explicitly.
                    Include input validation.
                    Use defensive programming techniques.""",
                    context=problem_spec
                )
            )
            
            # Ensemble to select/synthesize best solution
            candidate_solution = await self.ensemble(
                instruction="""Evaluate these solution approaches and select or synthesize the best one.
                Criteria:
                1. Correctness (must handle all edge cases)
                2. Efficiency (optimal algorithm choice)
                3. Readability (clear, maintainable code)
                4. Robustness (comprehensive error handling)
                Return a single, improved solution that combines the best aspects of each approach.""",
                contexts_list=solution_approaches
            )

        # Phase 3: Generate additional edge case tests
        edge_case_tests = await self.generate(
            instruction=f"""Generate 5 additional edge case test scenarios for this problem:
            Problem specification: {problem_spec}
            Consider:
            - Empty inputs
            - Single element inputs
            - Boundary values
            - Duplicate elements
            - Unusual data types
            - Maximum/minimum values
            Format as Python assert statements.""",
            context=problem_spec
        )

        # Phase 4: Validation and Iterative Refinement
        final_solution = candidate_solution
        max_retries = 3
        current_retry = 0
        
        while current_retry < max_retries:
            try:
                # Extract test cases from problem text
                test_case_extraction = await self.generate(
                    instruction="""Extract all test cases from the original problem.
                    Format them as a list of Python assert statements.
                    If no explicit tests, return empty list.""",
                    context=""
                )
                
                # Combine original and generated tests
                all_tests = f"{test_case_extraction}\n{edge_case_tests}"
                
                # Validate solution with programmer
                validation_result = await self.programmer(
                    instruction=f"""Execute this solution against the test cases:
                    Solution: {final_solution}
                    Test cases: {all_tests}
                    Return detailed results including any failures.""",
                    context=final_solution,
                    max_retries=1
                )
                
                # Check if validation passed
                if "error" not in validation_result.lower() and "fail" not in validation_result.lower():
                    break  # Success!
                
                # Revise based on validation feedback
                final_solution = await self.revise(
                    instruction=f"""Revise this solution based on validation feedback:
                    Current solution: {final_solution}
                    Validation feedback: {validation_result}
                    Problem specification: {problem_spec}
                    Fix all identified issues while maintaining solution quality.
                    Pay special attention to failing test cases.""",
                    context=final_solution
                )
                
                current_retry += 1
                
            except Exception as e:
                # Fallback revision on exception
                final_solution = await self.revise(
                    instruction=f"""Fix this solution which encountered an error:
                    Solution: {final_solution}
                    Error: {str(e)}
                    Problem specification: {problem_spec}
                    Make it more robust and error-resistant.""",
                    context=final_solution
                )
                current_retry += 1

        # Phase 5: Final Quality Assurance
        final_review = await self.generate(
            instruction=f"""Perform a senior engineer code review of this solution:
            Solution: {final_solution}
            Problem specification: {problem_spec}
            Check for:
            - Code smells or anti-patterns
            - Maintainability concerns
            - Performance bottlenecks
            - Missing edge cases
            - Style and readability
            Provide specific improvement suggestions if needed.""",
            context=final_solution
        )
        
        # Final revision based on code review
        final_solution = await self.revise(
            instruction=f"""Incorporate these code review suggestions:
            Current solution: {final_solution}
            Review feedback: {final_review}
            Problem specification: {problem_spec}
            Improve the solution while preserving correctness.
            Focus on maintainability and best practices.""",
            context=final_solution
        )

        return final_solution