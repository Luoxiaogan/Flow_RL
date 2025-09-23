# Workflow ID: mbppplus_161_0
# Benchmark: mbppplus
# Data Indices: [123, 46]

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

        # Phase 1: Problem Classification & Strategy Selection
        classification = await self.generate(
            instruction="""Analyze this programming problem in depth. Classify it by:
            - Primary domain (string, math, list, logic, etc.)
            - Required operations (splitting, summing, filtering, etc.)
            - Expected input/output types and edge cases
            - Complexity level (simple, moderate, complex)
            - Recommended solution approach (regex, comprehensions, recursion, etc.)
            - Potential pitfalls or ambiguities
            Output a structured analysis that will guide subsequent solution generation.""",
            context=""
        )

        # Phase 2: Conditional Decomposition (only if complex)
        subproblems = []
        if "complex" in classification.lower() or "ambiguous" in classification.lower():
            decomposition = await self.decompose(
                instruction="""Break this problem into minimal, independent subproblems.
                Each subproblem should be solvable in isolation and contribute directly to the final solution.
                Specify clear inputs/outputs for each and any dependencies between them.""",
                context=classification
            )
            subproblems = decomposition

        # Phase 3: Generate Multiple Solution Candidates in Parallel
        solution_instructions = [
            """Implement a solution using the most straightforward, idiomatic Python approach.
            Prioritize readability and use of built-in functions. Handle edge cases explicitly.
            Match the exact function signature and return type specified.""",
            
            """Implement a solution using an alternative algorithmic approach (e.g., if regex was natural, 
            use iterative parsing instead). Focus on robustness and comprehensive edge case handling.
            Include type checking and defensive programming where appropriate.""",
            
            """Implement a solution optimized for performance or minimalism. Use advanced Python features
            or clever one-liners if appropriate, but ensure correctness is not sacrificed.
            Document any non-obvious logic in comments (to be stripped later)."""
        ]

        # Generate base solutions
        base_solutions = await asyncio.gather(
            *[self.generate(
                instruction=f"""{instr}
                
                Problem Context:
                {classification}
                
                IMPORTANT: Return ONLY the function implementation with necessary imports inside.
                Use the EXACT function name from the problem. No explanations or markdown.""",
                context=""
            ) for instr in solution_instructions]
        )

        # Phase 4: Generate Synthetic Test Cases
        test_cases = await self.generate(
            instruction="""Generate 5 comprehensive test cases for this function, including:
            - Typical use cases
            - Edge cases (empty inputs, single elements, boundaries)
            - Error cases (if applicable)
            - Type variations
            Format as Python assert statements, one per line.""",
            context=classification
        )

        # Phase 5: Validate & Revise Solutions
        validated_solutions = []
        for i, solution in enumerate(base_solutions):
            current_solution = solution
            for attempt in range(3):  # Max 3 revision attempts
                try:
                    # Validate with programmer operator
                    validation = await self.programmer(
                        instruction=f"""Execute these test cases against the provided solution:
                        {test_cases}
                        
                        Solution to test:
                        {current_solution}
                        
                        Return 'PASS' if all tests pass, otherwise return specific error messages.""",
                        context=current_solution,
                        max_retries=1
                    )
                    
                    if "PASS" in validation:
                        validated_solutions.append(current_solution)
                        break
                    else:
                        # Revise based on errors
                        current_solution = await self.revise(
                            instruction=f"""Fix the solution based on these errors:
                            {validation}
                            
                            Ensure the solution:
                            - Matches exact function signature
                            - Handles all edge cases
                            - Returns correct data type
                            - Is syntactically valid Python
                            
                            Return ONLY the corrected function implementation.""",
                            context=current_solution
                        )
                except Exception as e:
                    # If programmer fails, try one more revision with exception info
                    if attempt < 2:
                        current_solution = await self.revise(
                            instruction=f"""The solution caused an execution error: {str(e)}
                            Rewrite to avoid this error while maintaining functionality.
                            Return ONLY the corrected function implementation.""",
                            context=current_solution
                        )
                    else:
                        break
            else:
                # If we exhausted attempts, still include for ensemble (might be best available)
                validated_solutions.append(current_solution)

        # Phase 6: Ensemble Selection
        if len(validated_solutions) > 1:
            final_solution = await self.ensemble(
                instruction="""Select the best solution based on:
                1. Correctness (passes all test cases)
                2. Simplicity and readability
                3. Efficiency and performance
                4. Adherence to specified return types
                5. Minimal external dependencies
                Return ONLY the selected function implementation, no explanations.""",
                contexts_list=validated_solutions
            )
        else:
            final_solution = validated_solutions[0] if validated_solutions else base_solutions[0]

        # Phase 7: Clean & Extract Final Code
        clean_code = await self.summarize(
            instruction="""Extract ONLY the Python function code from the text below.
            Remove all markdown, explanations, comments, and extra text.
            Return only the raw code starting from 'def' or 'import' statements.
            Ensure the code is syntactically complete and matches the required signature.""",
            context=final_solution
        )

        return clean_code