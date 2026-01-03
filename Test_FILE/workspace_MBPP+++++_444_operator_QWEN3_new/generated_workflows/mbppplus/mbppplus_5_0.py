# Workflow ID: mbppplus_5_0
# Benchmark: mbppplus
# Data Indices: [162, 205, 276]

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

    async def run_workflow(self):
        import asyncio
        import re

        # STEP 1: CLASSIFY PROBLEM TYPE AND EXTRACT CONSTRAINTS
        classification = await self.generate(
            instruction="""Analyze the problem text and classify it into one of these categories:
            - Sorting/Ordering Problems (e.g., sort strings, find min differences in arrays)
            - Sequential Traversal (e.g., max consecutive runs, pattern matching)
            - Set/Collection Operations (e.g., intersections, unions, filtering)
            - Mathematical Computations (e.g., arithmetic, number theory)
            - Validation/Logic Problems (e.g., condition checking, comparisons)
            
            Additionally, extract ALL explicit and implicit constraints:
            - Required input/output types (list, tuple, string, etc.)
            - Edge cases to handle (empty inputs, single elements, duplicates, negatives)
            - Performance or efficiency expectations
            - Order preservation requirements
            - Special conditions (case sensitivity, whitespace handling, etc.)
            
            Format your response as:
            CATEGORY: [category name]
            CONSTRAINTS:
            - [constraint 1]
            - [constraint 2]
            ...""",
            context=""
        )

        # STEP 2: GENERATE EDGE CASES BASED ON CLASSIFICATION
        edge_cases = await self.generate(
            instruction=f"""Based on the problem classification and constraints below, generate a comprehensive list of edge cases and boundary conditions that any robust solution must handle:
            
            {classification}
            
            Include at least:
            - Empty input cases
            - Single element cases
            - All duplicate elements
            - Boundary values (min/max, negatives, zeros)
            - Type edge cases (if applicable)
            - Order-dependent edge cases
            - Performance stress cases (if applicable)
            
            Format as numbered list with brief description of each edge case.""",
            context=classification
        )

        # STEP 3: PARALLEL SOLUTION GENERATION (DIAMOND PATTERN START)
        # Generate 3 different solution approaches in parallel
        solution_approaches = [
            "Approach 1: Direct and straightforward implementation focusing on clarity and correctness",
            "Approach 2: Optimized implementation focusing on efficiency and minimal operations",
            "Approach 3: Robust implementation with extensive edge case handling and defensive programming"
        ]

        solution_candidates = await asyncio.gather(
            *[self.generate(
                instruction=f"""Generate a complete Python function solution for the problem using {approach}.
                
                Problem Classification: {classification}
                Edge Cases to Handle: {edge_cases}
                
                Requirements:
                - Must handle ALL edge cases listed above
                - Must match exact function signature from problem
                - Must return correct data type (list, tuple, string, etc.)
                - Code must be clean, readable, and well-commented
                - Include brief comments explaining key logic decisions
                
                Return ONLY the function implementation with necessary imports, nothing else.""",
                context=""
            ) for approach in solution_approaches]
        )

        # STEP 4: VALIDATE EACH SOLUTION CANDIDATE
        validation_tasks = []
        for i, candidate in enumerate(solution_candidates):
            validation_task = self.generate(
                instruction=f"""Critically analyze the following solution candidate for correctness and robustness:
                
                Solution Candidate {i+1}:
                {candidate}
                
                Problem Classification: {classification}
                Required Edge Cases: {edge_cases}
                
                Check for:
                - Logical correctness for all edge cases
                - Proper handling of input/output types
                - Potential off-by-one errors
                - Missing edge case handling
                - Return type consistency
                - Code clarity and maintainability
                
                If any issues found, describe them specifically. If no issues, state "VALID".
                
                Format: "ISSUES: [list of issues]" or "VALID".""",
                context=candidate
            )
            validation_tasks.append(validation_task)
        
        validations = await asyncio.gather(*validation_tasks)

        # STEP 5: REVISE INVALID SOLUTIONS
        revised_solutions = []
        for i, (candidate, validation) in enumerate(zip(solution_candidates, validations)):
            if "VALID" not in validation.upper():
                revised = await self.revise(
                    instruction=f"""Revise the following solution to fix all identified issues:
                    
                    Original Solution:
                    {candidate}
                    
                    Validation Issues:
                    {validation}
                    
                    Problem Classification: {classification}
                    Edge Cases: {edge_cases}
                    
                    Requirements:
                    - Fix all identified issues while preserving core logic
                    - Maintain correct function signature
                    - Ensure all edge cases are properly handled
                    - Keep code clean and readable
                    - Return ONLY the function implementation with necessary imports""",
                    context=candidate
                )
                revised_solutions.append(revised)
            else:
                revised_solutions.append(candidate)

        # STEP 6: ENSEMBLE - SELECT OR SYNTHESIZE BEST SOLUTION
        final_solution = await self.ensemble(
            instruction=f"""Select the best solution from the candidates below, or synthesize a new solution combining the best aspects of multiple candidates.
            
            Selection Criteria:
            - Correctness (handles all edge cases)
            - Code clarity and readability
            - Efficiency (reasonable time/space complexity)
            - Robustness (defensive programming where appropriate)
            - Adherence to problem constraints and requirements
            
            Problem Classification: {classification}
            Edge Cases: {edge_cases}
            
            Return ONLY the final function implementation with necessary imports, nothing else.""",
            contexts_list=revised_solutions
        )

        # STEP 7: FINAL VALIDATION AND TYPE CHECKING
        final_validation = await self.generate(
            instruction=f"""Perform final validation on the selected solution:
            
            Solution:
            {final_solution}
            
            Verify:
            - Function signature matches exactly what's required
            - Return type is correct (list, tuple, string, etc.)
            - All edge cases from {edge_cases} are handled
            - No syntax errors or logical flaws
            - Code is clean and follows Python best practices
            
            If any issues found, return a revised version fixing them. Otherwise, return the solution unchanged.
            
            Return ONLY the function implementation with necessary imports.""",
            context=final_solution
        )

        # STEP 8: FINAL CLEANUP AND RETURN
        # Ensure the solution is clean and properly formatted
        cleaned_solution = await self.revise(
            instruction="""Clean up the solution code:
            - Remove any unnecessary comments or debug statements
            - Ensure proper Python formatting and style
            - Verify imports are only what's necessary
            - Ensure function signature is exactly as required
            - Return ONLY the function implementation with necessary imports, nothing else""",
            context=final_validation
        )

        return cleaned_solution