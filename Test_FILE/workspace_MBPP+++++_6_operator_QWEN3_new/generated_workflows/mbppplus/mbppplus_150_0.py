# Workflow ID: mbppplus_150_0
# Benchmark: mbppplus
# Data Indices: [103, 53]

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

        # STEP 1: Deep Problem Analysis & Classification
        problem_analysis = await self.generate(
            instruction="""Perform a comprehensive analysis of this programming problem. Your analysis must include:
            1. Function signature and expected input/output types
            2. Problem category (mathematical, string, list, logical, etc.)
            3. Key operations required (iteration, recursion, formula, validation, etc.)
            4. Potential edge cases (empty inputs, zero, negatives, large values, type mismatches)
            5. Performance considerations (time complexity, recursion depth, memory)
            6. Multiple viable solution strategies with pros/cons
            7. Any implicit constraints or assumptions in the problem statement
            8. Required return type and format (must match test cases exactly)
            
            Structure your response clearly with headings for each section. Be exhaustive - this analysis will guide all subsequent steps.""",
            context=""
        )

        # STEP 2: Parallel Strategy Generation
        strategy_tasks = [
            self.generate(
                instruction=f"""Based on this analysis:
                {problem_analysis}
                
                Generate a complete solution using an ITERATIVE approach. Include:
                - Input validation for edge cases
                - Clear variable names and comments
                - Exact function signature as specified
                - Return type matching test cases
                - No external dependencies unless absolutely necessary""",
                context=problem_analysis
            ),
            self.generate(
                instruction=f"""Based on this analysis:
                {problem_analysis}
                
                Generate a complete solution using a RECURSIVE approach (if applicable). Include:
                - Base case handling for edge cases
                - Recursive case with clear logic
                - Stack depth considerations (add warning if recursion may fail for large inputs)
                - Exact function signature and return type
                - Input validation if needed""",
                context=problem_analysis
            ),
            self.generate(
                instruction=f"""Based on this analysis:
                {problem_analysis}
                
                Generate a solution using the most DIRECT MATHEMATICAL FORMULA or built-in functions. Include:
                - Formula explanation in comments
                - Edge case handling
                - Type conversions if needed
                - Exact function signature
                - Optimizations for performance""",
                context=problem_analysis
            ),
            self.generate(
                instruction=f"""Based on this analysis:
                {problem_analysis}
                
                Generate a DEFENSIVE PROGRAMMING solution that:
                - Validates all inputs (type, range, etc.)
                - Handles all edge cases explicitly
                - Returns appropriate values or raises meaningful errors
                - Includes comprehensive comments
                - Matches exact function signature and return type
                - Prioritizes robustness over elegance""",
                context=problem_analysis
            )
        ]
        
        strategy_candidates = await asyncio.gather(*strategy_tasks)

        # STEP 3: Parallel Code Generation & Execution
        code_tasks = [
            self.programmer(
                instruction=f"""Convert this solution strategy into executable Python code:
                {candidate}
                
                Requirements:
                - Must use exact function name and parameters from problem
                - Must handle edge cases identified in analysis
                - Must return correct data type (int, float, list, etc.)
                - No print statements or side effects
                - Include minimal necessary imports
                - Code must be self-contained and runnable""",
                context=candidate,
                max_retries=3
            ) for candidate in strategy_candidates
        ]
        
        code_results = await asyncio.gather(*code_tasks)

        # STEP 4: Ensemble Selection of Best Solution
        best_solution = await self.ensemble(
            instruction="""Select the best solution from the candidates based on:
            1. Correctness (must pass basic test cases)
            2. Robustness (handles edge cases gracefully)
            3. Efficiency (prefer iterative over recursive for large inputs, O(1) over O(n) if possible)
            4. Code clarity and maintainability
            5. Adherence to exact function signature and return type
            
            If multiple solutions are correct, choose the most efficient and readable.
            If no solution is perfect, choose the one closest to requirements and note deficiencies.
            Return ONLY the selected code block (including function definition) - nothing else.""",
            contexts_list=code_results
        )

        # STEP 5: Refinement Loop (up to 2 iterations)
        current_solution = best_solution
        for refinement_round in range(2):
            validation_feedback = await self.generate(
                instruction=f"""Critically evaluate this solution:
                {current_solution}
                
                Check for:
                - Exact function signature match
                - Correct return type (must match test cases)
                - Edge case handling (zero, negatives, empty, large values)
                - Potential bugs or logical errors
                - Performance issues
                - Code style and readability
                
                If any issues found, describe them specifically. If perfect, say 'APPROVED'.""",
                context=current_solution
            )
            
            if "APPROVED" in validation_feedback.upper() and "ISSUE" not in validation_feedback.upper():
                break
                
            current_solution = await self.revise(
                instruction=f"""Revise this code based on feedback:
                {validation_feedback}
                
                Requirements:
                - Fix all identified issues
                - Maintain exact function signature
                - Ensure correct return type
                - Keep code clean and readable
                - Do not change core logic unless necessary
                - Return complete function code""",
                context=current_solution
            )

        # STEP 6: Final Sanitization
        final_code = await self.revise(
            instruction="""Ensure this code meets ALL requirements:
            1. Function name and parameters EXACTLY match problem specification
            2. Return type matches test cases (float, int, list, etc.)
            3. No extra output (print statements, debug info)
            4. Minimal necessary imports (if any)
            5. Clean, readable code with appropriate comments
            6. Handles edge cases appropriately
            
            Return ONLY the final function code - nothing before or after.""",
            context=current_solution
        )

        return final_code