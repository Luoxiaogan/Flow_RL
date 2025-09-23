# Workflow ID: mbppplus_60_0
# Benchmark: mbppplus
# Data Indices: [352, 30]

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

        # Step 1: Parallel problem classification from multiple perspectives
        classification_tasks = [
            self.generate(
                instruction="""Analyze the problem from a DATA STRUCTURE perspective:
                - What input types are involved (list, tuple, string, set, etc.)?
                - What output type is expected?
                - Are there nested structures or type conversions?
                - What are the key operations (filter, map, reduce, sort, etc.)?
                Format as bullet points.""",
                context=""
            ),
            self.generate(
                instruction="""Analyze the problem from an ALGORITHMIC PATTERNS perspective:
                - What algorithmic approach is likely needed (brute force, greedy, two-pointer, hash map, etc.)?
                - Are there hints of recursion or iteration?
                - What is the expected time/space complexity?
                - Are there mathematical formulas or sequences involved?
                Format as bullet points.""",
                context=""
            ),
            self.generate(
                instruction="""Analyze the problem from an EDGE CASE & ROBUSTNESS perspective:
                - What are potential edge cases (empty input, single element, duplicates, etc.)?
                - What input validation might be needed?
                - Are there boundary conditions or overflow risks?
                - What could cause the solution to fail?
                Format as bullet points.""",
                context=""
            )
        ]
        
        classifications = await asyncio.gather(*classification_tasks)
        
        # Step 2: Ensemble classifications into unified problem profile
        problem_profile = await self.ensemble(
            instruction="""Synthesize these three analyses into a comprehensive problem profile:
            - Combine insights about data structures, algorithms, and edge cases
            - Identify the 1-2 most critical algorithmic approaches
            - List the 3 most important edge cases to handle
            - Determine if the problem is simple (1-2 steps) or complex (3+ steps)
            - Output in structured JSON-like format with keys: data_types, algorithm_approach, edge_cases, complexity_score""",
            contexts_list=classifications
        )

        # Step 3: Conditional decomposition based on complexity
        if "complexity_score" in problem_profile and int(re.search(r'complexity_score\D+(\d)', problem_profile).group(1)) > 2:
            # Complex problem - decompose into subproblems
            decomposition = await self.decompose(
                instruction=f"""Based on this problem profile:
                {problem_profile}
                
                Decompose the solution into atomic, testable subproblems. Each subproblem should be:
                - Independently solvable
                - Have clear input/output
                - Include dependencies if needed
                Focus on: input validation, core logic, edge case handling, output formatting.""",
                context=problem_profile
            )
            
            # Generate solutions for each subproblem in parallel
            subproblem_solutions = []
            for sub in decomposition:
                solution = await self.generate(
                    instruction=f"""Solve this subproblem:
                    {sub['description']}
                    
                    Problem context: {problem_profile}
                    Return ONLY the code snippet for this subproblem, no explanations.""",
                    context=problem_profile
                )
                subproblem_solutions.append(solution)
            
            # Assemble scaffold and inject subproblem solutions
            scaffold = await self.programmer(
                instruction=f"""Generate a function scaffold for this problem:
                {problem_profile}
                
                Include placeholders for each subproblem solution. Use descriptive variable names.
                Return ONLY the code with placeholders like # SUBPROBLEM_1_HERE""",
                context=problem_profile,
                max_retries=1
            )
            
            # Revise scaffold by injecting subproblem solutions
            assembled_code = scaffold
            for i, solution in enumerate(subproblem_solutions):
                assembled_code = await self.revise(
                    instruction=f"""Inject this subproblem solution into the scaffold:
                    Solution: {solution}
                    Replace the appropriate placeholder. Ensure variable names and types are consistent.
                    Return the complete code with this subproblem integrated.""",
                    context=assembled_code
                )
        else:
            # Simple problem - generate end-to-end solution
            assembled_code = await self.generate(
                instruction=f"""Generate a complete, production-ready solution for this problem:
                {problem_profile}
                
                Requirements:
                - Handle all edge cases mentioned in profile
                - Match expected input/output types exactly
                - Include minimal but sufficient comments
                - No unnecessary imports or code
                Return ONLY the function implementation.""",
                context=problem_profile
            )

        # Step 4: Generate edge case tests
        edge_cases = await self.generate(
            instruction=f"""Based on the problem profile:
            {problem_profile}
            
            Generate 5 comprehensive edge case test scenarios. For each, provide:
            - Input description
            - Expected output
            - Why it's an edge case
            Format as Python assert statements.""",
            context=problem_profile
        )

        # Step 5: Iterative refinement with testing
        current_code = assembled_code
        for attempt in range(3):  # Max 3 attempts
            try:
                test_result = await self.programmer(
                    instruction=f"""Test this code against edge cases:
                    {edge_cases}
                    
                    Also validate against the original problem's test cases.
                    Return 'PASS' if all tests pass, otherwise return detailed error message.""",
                    context=current_code,
                    max_retries=1
                )
                
                if "PASS" in test_result:
                    break
                else:
                    # Revise based on errors
                    current_code = await self.revise(
                        instruction=f"""Fix the code based on these test failures:
                        {test_result}
                        
                        Problem profile: {problem_profile}
                        Edge cases: {edge_cases}
                        
                        Specific fixes needed:
                        - Address the exact errors mentioned
                        - Maintain correct return types
                        - Don't break existing functionality
                        Return the complete fixed code.""",
                        context=current_code
                    )
            except Exception as e:
                # Fallback revision on execution error
                current_code = await self.revise(
                    instruction=f"""The code failed to execute due to: {str(e)}
                    Make it syntactically correct and robust.
                    Problem profile: {problem_profile}
                    Return complete fixed code.""",
                    context=current_code
                )

        # Step 6: Final output formatting validation
        final_code = await self.revise(
            instruction=f"""Ensure this code meets all domain requirements:
            - Function name matches exactly
            - Return type is correct (list vs tuple vs set)
            - No extra prints or debug statements
            - Imports are minimal and inside function if needed
            - Code is clean and readable
            Problem profile: {problem_profile}
            Return the final code exactly as required.""",
            context=current_code
        )

        return final_code