# Workflow ID: mbppplus_51_0
# Benchmark: mbppplus
# Data Indices: [0, 151, 135]

# --- DO NOT IMPORT HERE ---
class Workflow:
    def __init__(self, config, problem) -> None:
        # --- DO NOT MODIFY THIS SECTION ---
        self.config = config
        self.problem_text = problem
        self.llm = create(config)
        
        self.generate = operator.Generate(self.llm, self.problem_text)
        self.revise = operator.Revise(self.llm, self.problem_text)
        self.summarize = operator.Summarize(self.llm, self.problem_text)
        self.ensemble = operator.Ensemble(self.llm, self.problem_text)

    async def run_workflow(self):
        """
        Universal workflow for programming problem solving.
        Uses parallel generation, validation, and ensemble selection.
        """
        import asyncio
        import re

        # Step 1: Extract test cases from problem text for validation
        test_case_extraction = await self.generate(
            instruction="""Extract all test cases (assert statements) from the problem text.
            Format them as a list of tuples: (function_call, expected_result)
            Example: [("max_chain_length([Pair(5,24),...], 4)", "3"), ...]
            Focus only on executable test cases shown in the problem.
            If no test cases are provided, return an empty list.
            Be precise about the exact function calls and expected values.""",
            context=""
        )

        # Step 2: Generate multiple solution approaches in parallel
        solution_approaches = [
            """Generate a direct implementation solution based on the reference solution pattern.
            Instructions:
            - Match the exact function signature provided
            - Handle all edge cases (empty inputs, single elements, boundaries)
            - Ensure correct return types (int, list, tuple, etc. as required)
            - Include necessary imports at the top of the function
            - Write clean, readable code with appropriate variable names
            - Follow Python best practices and PEP 8 guidelines
            - Do NOT include any test code or print statements
            - Return only the function implementation as specified
            - Pay special attention to type consistency and edge case handling""",
            
            """Generate a mathematical/formulaic solution approach.
            Instructions:
            - Look for mathematical patterns or closed-form solutions
            - Consider recurrence relations, combinatorial formulas, or algebraic simplifications
            - If applicable, use mathematical insights to optimize the solution
            - Still match the exact function signature provided
            - Handle edge cases mathematically (what happens when n=0, empty list, etc.)
            - Ensure numerical precision and correct data types
            - Include necessary imports for mathematical operations
            - Return only the function implementation
            - Document any mathematical assumptions in comments""",
            
            """Generate an algorithmic/iterative solution with comprehensive edge case handling.
            Instructions:
            - Use step-by-step algorithmic approach with clear logic
            - Consider all possible edge cases: empty inputs, single elements, duplicates, boundaries
            - Implement defensive programming with appropriate checks
            - Use descriptive variable names and clear control flow
            - Optimize for correctness first, then consider efficiency
            - Include necessary imports
            - Return only the function implementation
            - Add comments explaining complex logic or edge case handling"""
        ]

        # Generate solutions in parallel
        solution_tasks = [
            self.generate(instruction=approach, context="")
            for approach in solution_approaches
        ]
        solutions = await asyncio.gather(*solution_tasks)

        # Step 3: Validate each solution against test cases in parallel
        async def validate_solution(solution, index):
            validation_instruction = f"""Validate this solution against the extracted test cases.
            Solution index: {index}
            Extracted test cases: {test_case_extraction}
            
            Instructions:
            - Analyze if the solution would pass all provided test cases
            - Check for correct function signature and return types
            - Verify edge case handling (empty inputs, boundaries, etc.)
            - Identify any potential bugs or logical errors
            - Assess code quality, readability, and adherence to best practices
            - If test cases are available, specifically check against them
            - Return a detailed validation report including:
              1. Pass/fail status for each test case
              2. Edge case coverage assessment
              3. Code quality evaluation
              4. Specific issues found (if any)
              5. Confidence level in correctness (high/medium/low)"""
            
            return await self.generate(instruction=validation_instruction, context=solution)

        validation_tasks = [
            validate_solution(solution, i) for i, solution in enumerate(solutions)
        ]
        validations = await asyncio.gather(*validation_tasks)

        # Step 4: Revise solutions that show promise but have fixable issues
        async def revise_if_needed(solution, validation, index):
            if "fail" in validation.lower() or "error" in validation.lower() or "issue" in validation.lower():
                revision_instruction = f"""Revise this solution to fix identified issues.
                Original solution index: {index}
                Validation feedback: {validation}
                
                Instructions:
                - Address all specific issues mentioned in the validation
                - Maintain the original function signature and return type
                - Improve edge case handling based on feedback
                - Enhance code clarity if needed
                - Do NOT change the core algorithm unless necessary to fix correctness
                - Return only the revised function implementation
                - Include necessary imports
                - Ensure the solution is now robust against identified edge cases"""
                
                return await self.revise(instruction=revision_instruction, context=solution)
            else:
                return solution  # No revision needed

        revision_tasks = [
            revise_if_needed(solutions[i], validations[i], i) 
            for i in range(len(solutions))
        ]
        revised_solutions = await asyncio.gather(*revision_tasks)

        # Step 5: Ensemble - select the best solution with justification
        final_selection = await self.ensemble(
            instruction="""Select the best solution from the candidates and provide detailed justification.
            Consider these criteria in order of priority:
            1. Correctness: Passes all test cases and handles edge cases properly
            2. Code quality: Readability, maintainability, adherence to best practices
            3. Robustness: Comprehensive edge case handling and defensive programming
            4. Efficiency: Computational complexity and performance (secondary to correctness)
            
            For each solution, provide:
            - Summary of strengths and weaknesses
            - Assessment of test case coverage
            - Edge case handling evaluation
            - Code quality rating
            
            Then select the single best solution and explain why it's superior.
            Return ONLY the selected solution code (function implementation with imports).
            Do NOT include any additional text, explanations, or markdown formatting.""",
            contexts_list=revised_solutions
        )

        return final_selection