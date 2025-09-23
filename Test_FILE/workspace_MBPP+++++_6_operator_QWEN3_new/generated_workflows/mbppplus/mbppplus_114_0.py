# Workflow ID: mbppplus_114_0
# Benchmark: mbppplus
# Data Indices: [254, 202]

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

        # Step 1: Classify problem and extract metadata
        classification = await self.generate(
            instruction="""Thoroughly analyze the programming problem and extract the following metadata:
            1. Problem Category: Is this number theory, bit manipulation, string processing, array/list operations, mathematical computation, or logic/validation?
            2. Input/Output Specification: What are the exact input types and expected output types? Are there constraints on ranges or formats?
            3. Edge Cases: What edge cases must be handled? Consider: zero, negative numbers, empty inputs, single elements, maximum/minimum values, duplicates, boundary conditions.
            4. Algorithmic Approach: What are 2-3 potential solution strategies? Rank them by efficiency and simplicity.
            5. Decomposition Need: Can this problem be broken into independent subproblems? If yes, describe them briefly.
            6. Output Format: What is the exact required function signature and return type?
            Present your analysis in a structured JSON-like format for easy parsing.""",
            context=""
        )

        # Step 2: Enumerate edge cases (parallel with solution generation later)
        edge_case_task = asyncio.create_task(
            self.generate(
                instruction="""Based on the problem description, enumerate all possible edge cases and boundary conditions that a robust solution must handle. 
                Include: empty inputs, zero, negative numbers, single-element cases, maximum/minimum values, duplicates, type mismatches, and any domain-specific boundaries.
                Format as a bulleted list with brief explanations for each.""",
                context=""
            )
        )

        # Step 3: Conditional branching - check if decomposition is needed
        needs_decomposition = "decompos" in classification.lower() or "subproblem" in classification.lower()
        
        if needs_decomposition:
            # Decompose and solve subproblems
            subproblems = await self.decompose(
                instruction="""Break down the problem into the smallest meaningful subproblems. For each subproblem:
                - Clearly define what it solves
                - Specify its inputs and outputs
                - Note any dependencies on other subproblems
                - Suggest an optimal solution strategy""",
                context=classification
            )
            
            # Solve subproblems in parallel
            subproblem_solutions = []
            for subproblem in subproblems:
                solution = await self.programmer(
                    instruction=f"""Solve this subproblem:
                    {subproblem['description']}
                    
                    Context from problem classification:
                    {classification}
                    
                    Ensure your solution handles all edge cases and matches the required output format.""",
                    context="",
                    max_retries=2
                )
                subproblem_solutions.append(solution)
            
            # Recompose solutions
            final_solution = await self.generate(
                instruction=f"""Integrate the following subproblem solutions into a complete, cohesive solution:
                {chr(10).join(subproblem_solutions)}
                
                Ensure the final function matches the exact signature required and handles all edge cases identified in:
                {await edge_case_task}""",
                context=""
            )
        else:
            # Generate multiple solution candidates in parallel
            solution_tasks = [
                asyncio.create_task(
                    self.programmer(
                        instruction=f"""Implement a solution using this strategy:
                        Strategy 1: Direct mathematical/bit manipulation approach - focus on efficiency and minimal operations.
                        
                        Problem context:
                        {classification}
                        
                        Must handle these edge cases:
                        {await edge_case_task}""",
                        context="",
                        max_retries=2
                    )
                ),
                asyncio.create_task(
                    self.programmer(
                        instruction=f"""Implement a solution using this strategy:
                        Strategy 2: Iterative/brute force approach with clear logic - prioritize readability and correctness over performance.
                        
                        Problem context:
                        {classification}
                        
                        Must handle these edge cases:
                        {await edge_case_task}""",
                        context="",
                        max_retries=2
                    )
                )
            ]
            
            solution_candidates = await asyncio.gather(*solution_tasks)
            
            # Ensemble selection of best solution
            final_solution = await self.ensemble(
                instruction=f"""Evaluate these candidate solutions and select the best one based on:
                1. Correctness: Does it handle all edge cases from {await edge_case_task}?
                2. Efficiency: Is it computationally optimal?
                3. Code Quality: Is it clean, readable, and well-structured?
                4. Format Compliance: Does it match the required function signature exactly?
                
                If no solution is perfect, synthesize a new solution combining the best elements of each.
                
                Problem classification for context:
                {classification}""",
                contexts_list=solution_candidates
            )

        # Validation and refinement loop (up to 3 iterations)
        current_solution = final_solution
        for iteration in range(3):
            validation = await self.generate(
                instruction=f"""Critically validate this solution:
                {current_solution}
                
                Check for:
                1. Logical correctness - simulate key test cases including edge cases from {await edge_case_task}
                2. Syntax and runtime errors
                3. Compliance with required function signature
                4. Handling of all edge cases
                5. Efficiency concerns
                
                If any issues are found, describe them specifically. If no issues, respond with 'VALIDATED'.""",
                context=current_solution
            )
            
            if "VALIDATED" in validation or "validated" in validation:
                break
            else:
                current_solution = await self.revise(
                    instruction=f"""Revise the solution to fix these issues:
                    {validation}
                    
                    Maintain the exact function signature and ensure all edge cases are handled.
                    Prioritize correctness over elegance.""",
                    context=current_solution
                )

        # Final formatting - extract only the function code
        formatted_solution = await self.revise(
            instruction="""Extract ONLY the Python function implementation from the text below. 
            Requirements:
            - Include all necessary imports at the top of the function if needed
            - Use the EXACT function name and parameter names as specified in the problem
            - Preserve the function signature exactly
            - Return the appropriate data type
            - Remove any explanations, markdown, or extra text
            - Do NOT wrap in any outer function or class
            - Output ONLY the function code, nothing else""",
            context=current_solution
        )

        # Clean up any remaining markdown or extra text
        code_lines = []
        in_code_block = False
        for line in formatted_solution.split('\n'):
            if line.strip().startswith('