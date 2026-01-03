# Workflow ID: mbppplus_107_0
# Benchmark: mbppplus
# Data Indices: [351, 98]

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

        # Step 1: Classify problem type and extract key constraints
        classification = await self.generate(
            instruction="""Perform deep problem classification:
            1. Identify primary domain: Is this combinatorics, string manipulation, number theory, or logic?
            2. Extract explicit constraints: input types, output format, edge cases mentioned.
            3. Infer implicit constraints: What edge cases are likely? (e.g., empty inputs, zeros, negatives, overflow)
            4. Determine solution approach category: Should this use DP, greedy, math identities, or brute force?
            5. List required output type: integer, string, list, tuple, or special values like "Not Possible".
            Output in JSON format with keys: domain, constraints, approach, output_type.""",
            context=""
        )

        # Step 2: Decompose into subproblems
        decomposition = await self.decompose(
            instruction="""Break this problem into minimal, ordered subproblems:
            - Each subproblem should be independently solvable
            - Specify dependencies between subproblems
            - Include edge case handling as explicit subproblems
            - Prioritize subproblems that reduce computational complexity
            Format each subproblem with clear ID, description, and dependencies.""",
            context=classification
        )

        # Step 3: Generate multiple solution strategies in parallel
        strategy_instructions = [
            """Develop a mathematically optimized solution:
            - Use known identities or theorems to reduce computation
            - Prioritize O(1) or O(log n) approaches if possible
            - Handle modulo arithmetic carefully if applicable
            - Include detailed comments explaining mathematical reasoning""",
            
            """Develop a dynamic programming or iterative solution:
            - Focus on step-by-step state transitions
            - Use memoization or tabulation as appropriate
            - Ensure space efficiency
            - Document recurrence relations or state update rules""",
            
            """Develop a direct/brute force solution with edge case guards:
            - Prioritize clarity and correctness over performance
            - Include explicit checks for all edge cases
            - Use defensive programming with input validation
            - Add comprehensive comments for maintainability"""
        ]

        strategy_tasks = [
            self.generate(
                instruction=f"""{instr}
                
                Problem Classification Context:
                {classification}
                
                Subproblem Decomposition:
                {[sub['description'] for sub in decomposition]}
                
                Generate complete, self-contained Python code that solves the problem.
                The code MUST:
                - Match the exact function signature from the problem
                - Handle all edge cases (empty, single element, zeros, negatives, etc.)
                - Return correct data type (int, str, list, etc.)
                - Include no extra output or print statements
                - Be ready for direct execution""",
                context=""
            ) for instr in strategy_instructions
        ]

        candidate_solutions = await asyncio.gather(*strategy_tasks)

        # Step 4: Validate and refine each candidate
        refined_candidates = []
        for i, candidate in enumerate(candidate_solutions):
            # First validation attempt
            validation = await self.programmer(
                instruction=f"""Execute this code against comprehensive test cases including:
                - Basic examples from problem
                - Edge cases: empty inputs, single elements, zeros, maximum values
                - Boundary conditions
                - Invalid inputs (if applicable)
                Return execution results and any errors.
                
                If code fails, identify specific failure cases and suggest fixes.
                If code passes, verify output type and format match requirements.""",
                context=candidate,
                max_retries=1
            )
            
            # If validation fails, attempt one revision
            if "error" in validation.lower() or "exception" in validation.lower():
                revised = await self.revise(
                    instruction=f"""Fix the code based on validation feedback:
                    Validation Results: {validation}
                    
                    Requirements:
                    - Must handle all edge cases identified in validation
                    - Must maintain correct function signature
                    - Must return correct data type
                    - Must be efficient and clean
                    
                    Return only the corrected Python code.""",
                    context=candidate
                )
                refined_candidates.append(revised)
            else:
                refined_candidates.append(candidate)

        # Step 5: Ensemble - select best solution
        best_solution = await self.ensemble(
            instruction="""Select the best solution based on:
            1. Correctness: Passes all test cases including edge cases
            2. Efficiency: Optimal time/space complexity
            3. Robustness: Handles edge cases explicitly
            4. Code quality: Clean, well-commented, maintainable
            5. Type safety: Returns correct data type as specified
            
            If multiple solutions are equally good, prefer the most efficient.
            Return only the selected Python code - no explanations.""",
            contexts_list=refined_candidates
        )

        # Step 6: Final verification and cleanup
        final_code = await self.revise(
            instruction="""Final code cleanup and verification:
            - Remove any debug prints or extra output
            - Ensure function signature exactly matches problem
            - Verify all edge cases are handled
            - Optimize imports (only include necessary ones)
            - Format code to PEP8 standards
            - Return ONLY the final function implementation with imports""",
            context=best_solution
        )

        return final_code