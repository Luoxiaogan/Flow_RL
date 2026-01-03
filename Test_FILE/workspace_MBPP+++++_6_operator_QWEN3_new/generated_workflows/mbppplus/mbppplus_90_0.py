# Workflow ID: mbppplus_90_0
# Benchmark: mbppplus
# Data Indices: [42, 269]

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

        # Step 1: Deep problem analysis - understand type, constraints, edge cases
        problem_analysis = await self.generate(
            instruction="""Perform comprehensive problem analysis:
            1. Classify problem type: Is it string pattern matching, numerical computation, 
               data structure manipulation, logical validation, or other?
            2. Identify input/output types: What data types are involved? What should be returned?
            3. Extract implicit constraints: Are there edge cases mentioned or implied? 
               Consider empty inputs, single elements, boundary values, type conversions.
            4. Determine solution approach: Should this use regex, filtering, iteration, 
               mathematical operations, or other techniques?
            5. Anticipate potential pitfalls: What are common mistakes for this type of problem?
            6. Generate 3-5 hypothetical test cases including edge cases.
            Format your response as a structured JSON with keys: problem_type, input_type, 
            output_type, constraints, approach, pitfalls, test_cases.""",
            context=""
        )

        # Step 2: Conditional branching based on problem type
        if "string" in problem_analysis.lower() or "pattern" in problem_analysis.lower() or "regex" in problem_analysis.lower():
            # String/pattern matching path
            # Generate multiple solution perspectives in parallel
            pattern_solutions = await asyncio.gather(
                self.generate(
                    instruction=f"""Based on analysis: {problem_analysis}
                    Generate a regex-based solution. Focus on:
                    - Correct pattern construction
                    - Boundary conditions (word boundaries, anchors)
                    - Return value format matching examples
                    - Include comprehensive comments explaining pattern logic""",
                    context=""
                ),
                self.generate(
                    instruction=f"""Based on analysis: {problem_analysis}
                    Generate a string-manipulation solution without regex. Focus on:
                    - Iterative character analysis
                    - Edge case handling
                    - Clear, readable logic
                    - Matching expected output format""",
                    context=""
                ),
                self.generate(
                    instruction=f"""Based on analysis: {problem_analysis}
                    Generate a hybrid solution combining multiple techniques. Focus on:
                    - Robustness across edge cases
                    - Performance considerations
                    - Elegant, maintainable code
                    - Comprehensive test coverage""",
                    context=""
                )
            )
            
            # Synthesize best solution
            final_solution = await self.ensemble(
                instruction="""Select and synthesize the best solution:
                1. Prioritize correctness above all else
                2. Ensure solution handles all edge cases identified in analysis
                3. Match expected return type and format exactly
                4. Prefer simpler, more readable solutions when correctness is equal
                5. Combine strengths from multiple approaches if beneficial
                Return only the final code implementation with necessary imports.""",
                contexts_list=pattern_solutions
            )
            
        elif "numerical" in problem_analysis.lower() or "sum" in problem_analysis.lower() or "filter" in problem_analysis.lower():
            # Numerical/computation path
            # Decompose into subproblems
            decomposition = await self.decompose(
                instruction=f"""Based on analysis: {problem_analysis}
                Break this problem into logical subproblems:
                1. Data filtering/transformation step
                2. Computation/aggregation step
                3. Edge case handling step
                4. Return value formatting step
                Each subproblem should be independently solvable and clearly defined.""",
                context=""
            )
            
            # Solve subproblems in sequence
            current_context = ""
            for subproblem in decomposition:
                sub_solution = await self.programmer(
                    instruction=f"""Solve this subproblem: {subproblem['description']}
                    Context from previous steps: {current_context}
                    Analysis context: {problem_analysis}
                    Ensure solution is type-safe and handles edge cases.
                    Return only the code implementation for this subproblem.""",
                    context=current_context
                )
                current_context += f"\nSubproblem {subproblem['id']} solution: {sub_solution}"
            
            # Generate final integrated solution
            final_solution = await self.generate(
                instruction=f"""Integrate all subproblem solutions into final implementation:
                Subproblem solutions: {current_context}
                Problem analysis: {problem_analysis}
                Ensure:
                1. Correct function signature matching original problem
                2. Proper handling of all edge cases
                3. Return type matches expected output
                4. Code is clean, efficient, and well-commented
                Return only the final code implementation with necessary imports.""",
                context=current_context
            )
            
        else:
            # Default comprehensive approach for other problem types
            # Generate initial solution attempt
            initial_solution = await self.programmer(
                instruction=f"""Based on analysis: {problem_analysis}
                Generate a complete solution. Focus on:
                - Correct implementation matching problem requirements
                - Handling all identified edge cases
                - Matching expected return type and format
                - Clean, readable code with appropriate comments""",
                context=""
            )
            
            # Validate and refine solution
            validation = await self.generate(
                instruction=f"""Critically validate this solution: {initial_solution}
                Against analysis: {problem_analysis}
                Check for:
                1. Correctness for all edge cases
                2. Type consistency
                3. Performance efficiency
                4. Code clarity and maintainability
                5. Match with expected output format
                Return detailed validation report with specific improvements needed.""",
                context=initial_solution
            )
            
            # Revise based on validation
            final_solution = await self.revise(
                instruction=f"""Improve this solution based on validation: {validation}
                Requirements:
                1. Fix all identified issues
                2. Maintain correct function signature
                3. Ensure robust edge case handling
                4. Optimize for clarity and efficiency
                5. Return only the final code implementation with necessary imports.""",
                context=initial_solution
            )

        # Final safety check and cleanup
        cleaned_solution = await self.revise(
            instruction="""Final cleanup and validation:
            1. Ensure code contains ONLY the function implementation with necessary imports
            2. Verify function name matches original problem exactly
            3. Confirm return type matches expected output
            4. Remove any extraneous text, comments, or explanations
            5. Ensure code is syntactically correct and follows Python best practices
            Return ONLY the cleaned code implementation.""",
            context=final_solution
        )
        
        return cleaned_solution