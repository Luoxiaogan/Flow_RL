# Workflow ID: mbppplus_151_0
# Benchmark: mbppplus
# Data Indices: [85, 337]

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
        import re
        
        try:
            # Phase 1: Parallel Problem Analysis from Multiple Perspectives
            analysis_tasks = [
                self.generate(
                    instruction="""Perform mathematical/algorithmic analysis:
                    1. Identify the core algorithmic pattern needed (hashing, sorting, two-pointer, etc.)
                    2. Determine time/space complexity requirements
                    3. Suggest optimal data structures
                    4. Outline step-by-step approach
                    5. Consider mathematical properties that could simplify the solution""",
                    context=""
                ),
                self.generate(
                    instruction="""Perform edge case analysis:
                    1. List all potential edge cases (empty inputs, single elements, duplicates, etc.)
                    2. Identify boundary conditions
                    3. Consider type mismatches or unexpected input formats
                    4. Think about performance edge cases (very large inputs, etc.)
                    5. Suggest how to handle each edge case""",
                    context=""
                ),
                self.generate(
                    instruction="""Perform type and format requirements analysis:
                    1. Extract exact input parameter types and constraints
                    2. Determine required return type and format
                    3. Note any string formatting requirements
                    4. Identify if order preservation is required
                    5. Document any implicit type conversions needed""",
                    context=""
                )
            ]
            
            # Execute analyses in parallel
            analysis_results = await asyncio.gather(*analysis_tasks)
            combined_analysis = "\n\n".join([
                f"MATHEMATICAL ANALYSIS:\n{analysis_results[0]}",
                f"EDGE CASE ANALYSIS:\n{analysis_results[1]}",
                f"TYPE/FORMAT ANALYSIS:\n{analysis_results[2]}"
            ])
            
            # Phase 2: Generate Multiple Solution Strategies in Parallel
            solution_strategies = [
                """Strategy 1: Use Python built-in functions and data structures
                - Leverage Counter, defaultdict, or other collections
                - Use list comprehensions and built-in methods
                - Focus on readability and Pythonic style""",
                
                """Strategy 2: Manual implementation with explicit loops
                - Implement algorithms from scratch
                - Focus on educational clarity and step-by-step logic
                - Include detailed comments explaining each step""",
                
                """Strategy 3: Optimized implementation
                - Focus on performance and efficiency
                - Use appropriate data structures for optimal complexity
                - Consider space-time tradeoffs
                - Include complexity analysis in comments"""
            ]
            
            solution_tasks = [
                self.generate(
                    instruction=f"""Generate a complete Python solution using this strategy:
                    {strategy}
                    
                    Based on this comprehensive analysis:
                    {combined_analysis}
                    
                    Requirements:
                    - Use EXACT function signature from problem
                    - Handle ALL edge cases identified in analysis
                    - Match required return type and format exactly
                    - Include necessary imports
                    - Write clean, well-commented code
                    - Return ONLY the function implementation (no test cases or examples)""",
                    context=combined_analysis
                ) for strategy in solution_strategies
            ]
            
            # Execute solution generation in parallel
            proposed_solutions = await asyncio.gather(*solution_tasks)
            
            # Phase 3: Execute and Validate Solutions
            execution_tasks = [
                self.programmer(
                    instruction=f"""Execute this solution and validate correctness:
                    {solution}
                    
                    Test with various inputs including edge cases.
                    Return the code and any execution results or errors.""",
                    context=solution
                ) for solution in proposed_solutions
            ]
            
            execution_results = await asyncio.gather(*execution_tasks, return_exceptions=True)
            
            # Filter successful executions
            successful_solutions = []
            failed_attempts = []
            
            for i, result in enumerate(execution_results):
                if isinstance(result, Exception) or "error" in str(result).lower():
                    failed_attempts.append({
                        "solution": proposed_solutions[i],
                        "error": str(result)
                    })
                else:
                    successful_solutions.append({
                        "solution": proposed_solutions[i],
                        "execution": result
                    })
            
            # Phase 4: Handle Failures and Refine
            if failed_attempts and successful_solutions:
                # Revise successful solutions based on failure analysis
                failure_summary = "\n\n".join([
                    f"FAILED SOLUTION:\n{attempt['solution']}\nERROR: {attempt['error']}"
                    for attempt in failed_attempts
                ])
                
                revision_tasks = [
                    self.revise(
                        instruction=f"""Improve this solution based on failure analysis:
                        {failure_summary}
                        
                        Incorporate lessons from failed attempts to make this solution more robust.
                        Specifically address any edge cases or issues revealed by the failures.
                        Maintain the core approach but enhance reliability and correctness.""",
                        context=solution["solution"]
                    ) for solution in successful_solutions
                ]
                
                revised_solutions = await asyncio.gather(*revision_tasks)
                final_solutions = revised_solutions
            elif successful_solutions:
                final_solutions = [solution["solution"] for solution in successful_solutions]
            else:
                # All solutions failed - fallback to decomposition
                decomposition = await self.decompose(
                    instruction="""Break this problem into fundamental subproblems:
                    1. Identify atomic operations needed
                    2. Define clear dependencies between subproblems
                    3. Specify input/output for each subproblem
                    4. Consider which subproblems can be solved independently
                    5. Outline how solutions will be combined""",
                    context=combined_analysis
                )
                
                # Generate solution based on decomposition
                decomposition_context = json.dumps(decomposition, indent=2)
                fallback_solution = await self.generate(
                    instruction=f"""Generate a solution based on this decomposition:
                    {decomposition_context}
                    
                    Implement each subproblem step by step.
                    Ensure proper integration of subproblem solutions.
                    Handle all edge cases identified in earlier analysis.
                    Return ONLY the function implementation.""",
                    context=decomposition_context
                )
                
                final_solutions = [fallback_solution]
            
            # Phase 5: Ensemble - Select Best Solution
            if len(final_solutions) > 1:
                best_solution = await self.ensemble(
                    instruction="""Select the best solution based on:
                    1. Correctness (handles all edge cases)
                    2. Efficiency (optimal time/space complexity)
                    3. Code clarity and maintainability
                    4. Adherence to requirements (exact function signature, return type)
                    5. Robustness (error handling, input validation)
                    
                    Return the complete function implementation of the best solution.
                    If multiple solutions are equally good, synthesize a hybrid solution
                    combining the best aspects of each.""",
                    contexts_list=final_solutions
                )
            else:
                best_solution = final_solutions[0]
            
            # Final cleanup and formatting
            cleaned_solution = await self.revise(
                instruction="""Final cleanup and formatting:
                1. Ensure EXACT function signature from original problem
                2. Verify all necessary imports are included
                3. Remove any test cases, examples, or extra text
                4. Format code according to PEP 8 guidelines
                5. Ensure return type matches requirements exactly
                6. Remove any unnecessary comments or debug statements
                7. Return ONLY the function implementation (no markdown, no explanations)""",
                context=best_solution
            )
            
            return cleaned_solution
            
        except Exception as e:
            # Fallback: Direct programmer attempt if workflow fails
            try:
                direct_solution = await self.programmer(
                    instruction="""Generate and execute a solution to this problem.
                    Focus on correctness and handling edge cases.
                    Return the complete function implementation.""",
                    context=""
                )
                return direct_solution
            except Exception as fallback_error:
                # Last resort: Simple generate attempt
                return await self.generate(
                    instruction="""Generate a Python function that solves this problem.
                    Include necessary imports.
                    Handle edge cases.
                    Match required function signature and return type.
                    Return ONLY the function implementation.""",
                    context=""
                )