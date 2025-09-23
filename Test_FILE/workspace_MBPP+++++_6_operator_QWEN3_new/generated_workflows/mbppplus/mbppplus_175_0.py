# Workflow ID: mbppplus_175_0
# Benchmark: mbppplus
# Data Indices: [220, 275]

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

        # Step 1: Deep problem classification and requirement extraction
        classification = await self.generate(
            instruction="""Perform a comprehensive analysis of this programming problem. Answer the following in structured detail:
            1. What are the exact input types and structures? (e.g., dict, int, list, string)
            2. What is the expected output type and format?
            3. What core operation is being performed? (e.g., merging, computing, filtering, transforming)
            4. Are there any explicit or implicit constraints? (e.g., handle duplicates, preserve order, efficiency requirements)
            5. What edge cases must be considered? (e.g., empty inputs, single elements, type mismatches, boundary values)
            6. Is this primarily a mathematical, data structure, string manipulation, or logical problem?
            7. What Python constructs or algorithms are likely needed? (e.g., loops, recursion, built-in functions, custom logic)
            Format your response as a clear, numbered list with detailed explanations for each point.""",
            context=""
        )

        # Step 2: Parallel analysis threads for robust understanding
        analysis_tasks = [
            self.generate(
                instruction="""Focus exclusively on mathematical and algorithmic aspects:
                - Identify any numerical computations, formulas, or sequences involved
                - Determine if standard algorithms (GCD, LCM, sorting, etc.) apply
                - Suggest mathematical optimizations or formula-based solutions
                - Highlight potential precision, overflow, or performance issues""",
                context=classification
            ),
            self.generate(
                instruction="""Focus exclusively on data structure and type handling:
                - Analyze input/output type transformations required
                - Identify potential type conflicts or conversion needs
                - Suggest appropriate data structures (dict, set, list, tuple) and their operations
                - Highlight mutability, ordering, or uniqueness requirements""",
                context=classification
            ),
            self.generate(
                instruction="""Focus exclusively on edge cases and robustness:
                - List all possible edge cases (empty, single element, maximum/minimum values, duplicates, type variations)
                - Suggest defensive programming techniques
                - Identify potential failure points and error conditions
                - Recommend validation or input sanitization steps""",
                context=classification
            )
        ]
        
        math_analysis, data_analysis, edge_analysis = await asyncio.gather(*analysis_tasks)

        # Step 3: Synthesize analyses into unified problem profile
        problem_profile = await self.ensemble(
            instruction="""Synthesize the three analytical perspectives into a unified problem-solving profile:
            1. Combine the mathematical, data structure, and edge case analyses into a coherent strategy
            2. Resolve any contradictions between analyses
            3. Prioritize solution approaches based on problem requirements
            4. Flag any remaining uncertainties or ambiguities
            5. Recommend the most appropriate solution paradigm (e.g., direct computation, iterative refinement, recursive approach)
            Output a comprehensive, actionable plan for solving the problem that incorporates all perspectives.""",
            contexts_list=[math_analysis, data_analysis, edge_analysis]
        )

        # Step 4: Generate multiple solution candidates
        solution_candidates = await asyncio.gather(
            self.generate(
                instruction=f"""Generate a direct, straightforward solution based on the problem profile:
                - Implement the most obvious approach first
                - Focus on correctness over optimization
                - Include basic edge case handling
                - Follow exact function signature requirements
                Problem Profile: {problem_profile}""",
                context=problem_profile
            ),
            self.generate(
                instruction=f"""Generate an optimized or alternative solution based on the problem profile:
                - Consider performance, memory, or elegance improvements
                - Use built-in functions or libraries where appropriate
                - Handle edge cases more comprehensively
                - Follow exact function signature requirements
                Problem Profile: {problem_profile}""",
                context=problem_profile
            )
        )

        # Step 5: Validate and refine solutions through iterative testing
        final_solution = solution_candidates[0]  # Start with first candidate
        for i in range(3):  # Maximum 3 refinement iterations
            try:
                # Test solution with programmer operator
                test_result = await self.programmer(
                    instruction=f"""Test this solution against the problem requirements:
                    - Execute against provided test cases
                    - Check for type correctness and edge case handling
                    - Identify any errors, exceptions, or mismatches
                    - Return detailed feedback for improvement""",
                    context=final_solution,
                    max_retries=1
                )
                
                # Check if solution passed all tests
                if "error" not in test_result.lower() and "exception" not in test_result.lower() and "fail" not in test_result.lower():
                    break  # Solution is acceptable
                
                # Refine solution based on test feedback
                final_solution = await self.revise(
                    instruction=f"""You are a senior Python developer reviewing code. Improve this solution based on the test feedback:
                    - Fix all identified errors and edge case failures
                    - Maintain exact function signature requirements
                    - Ensure type consistency and robust error handling
                    - Optimize only if it doesn't compromise correctness
                    Test Feedback: {test_result}""",
                    context=final_solution
                )
            except Exception as e:
                # If programmer fails, try to refine based on exception
                final_solution = await self.revise(
                    instruction=f"""The solution encountered an execution error. Fix the code to handle this gracefully:
                    Error: {str(e)}
                    - Ensure all edge cases are handled
                    - Add appropriate error checking or input validation
                    - Maintain exact function signature requirements""",
                    context=final_solution
                )

        # Step 6: Final cleanup and formatting to match exact requirements
        cleaned_solution = await self.revise(
            instruction="""Extract ONLY the function implementation that matches the required signature. Follow these rules exactly:
            1. Remove all markdown, explanations, or wrapper code
            2. Include only necessary imports INSIDE the function if required
            3. Use the EXACT function name and parameter names from the problem
            4. Return the appropriate data type as shown in test cases
            5. Handle empty inputs and edge cases appropriately
            6. Output ONLY the raw code block with no additional text or formatting
            7. Ensure the code is syntactically correct and ready to execute""",
            context=final_solution
        )

        # Step 7: Final validation and confidence check
        confidence_check = await self.generate(
            instruction=f"""Rate your confidence (1-10) that this solution handles ALL edge cases and requirements:
            - 10: Absolutely confident, handles all edge cases, matches specification exactly
            - 7-9: Confident but minor edge cases might need attention
            - 4-6: Some concerns about edge cases or specification compliance
            - 1-3: Major concerns, likely to fail on unseen test cases
            Solution: {cleaned_solution}
            Also list any remaining concerns or potential failure points.""",
            context=cleaned_solution
        )

        # If confidence is low, attempt one final decomposition and re-solution
        if any(phrase in confidence_check.lower() for phrase in ["1", "2", "3", "4", "5", "concern", "fail", "issue", "problem"]):
            # Decompose problem into subproblems
            subproblems = await self.decompose(
                instruction="""Break this problem down into the smallest possible atomic subproblems:
                - Each subproblem should be independently solvable
                - Identify dependencies between subproblems
                - Focus on edge cases and boundary conditions as separate subproblems
                - Include type handling and validation as explicit subproblems""",
                context=cleaned_solution
            )
            
            # Solve each subproblem independently
            subproblem_solutions = []
            for subproblem in subproblems:
                sub_solution = await self.programmer(
                    instruction=f"""Solve this atomic subproblem:
                    {subproblem['description']}
                    - Handle all edge cases for this subproblem
                    - Return appropriate data type
                    - Keep solution minimal and focused""",
                    context="",
                    max_retries=2
                )
                subproblem_solutions.append(sub_solution)
            
            # Reassemble solution from subproblems
            reassembled = await self.generate(
                instruction=f"""Reassemble these subproblem solutions into a complete solution:
                Subproblems and solutions: {subproblem_solutions}
                - Integrate solutions while maintaining correct data flow
                - Ensure overall solution matches required function signature
                - Add any necessary glue code or coordination logic
                - Output ONLY the final function implementation""",
                context=str(subproblem_solutions)
            )
            
            # Final cleanup
            cleaned_solution = await self.revise(
                instruction="""Extract ONLY the function implementation that matches the required signature. Follow these rules exactly:
                1. Remove all markdown, explanations, or wrapper code
                2. Include only necessary imports INSIDE the function if required
                3. Use the EXACT function name and parameter names from the problem
                4. Return the appropriate data type as shown in test cases
                5. Handle empty inputs and edge cases appropriately
                6. Output ONLY the raw code block with no additional text or formatting
                7. Ensure the code is syntactically correct and ready to execute""",
                context=reassembled
            )

        return cleaned_solution