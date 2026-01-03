# Workflow ID: mbppplus_9_0
# Benchmark: mbppplus
# Data Indices: [107, 101, 252]

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

        # Step 1: Meta-Analysis - Classify problem and extract critical constraints
        analysis_instruction = """
        Perform deep structural analysis of the programming problem:
        1. Extract the exact function signature (name, parameters, return type expectations)
        2. Classify problem type: string manipulation, mathematical computation, algorithmic optimization, or data structure operation
        3. Identify explicit and implicit edge cases: empty inputs, single elements, type boundaries, duplicates, order preservation needs
        4. Infer required data structures and type conversions (list vs tuple vs set)
        5. Note any efficiency constraints or algorithmic hints in the problem description
        6. Predict potential failure points in naive implementations
        Output as structured bullet points with clear section headers.
        """
        problem_analysis = await self.generate(instruction=analysis_instruction, context="")

        # Step 2: Parallel Solution Generation - Three distinct approaches
        solution_instructions = [
            """
            Generate a SIMPLE, READABLE solution focusing on:
            - Direct translation of problem description into code
            - Clear variable names and minimal complexity
            - Explicit handling of identified edge cases from analysis
            - Include necessary imports INSIDE the function if needed
            - Match exact function signature and return type
            """,
            """
            Generate an EFFICIENT, ROBUST solution focusing on:
            - Algorithmic optimization (avoid O(n^2) if possible)
            - Defensive programming (validate inputs, handle edge cases)
            - Use of appropriate data structures for performance
            - Include necessary imports INSIDE the function if needed
            - Match exact function signature and return type
            """,
            """
            Generate a REFERENCE-INSPIRED solution focusing on:
            - Mimicking the style and structure of reference solutions when available
            - Incorporating domain-specific patterns (e.g., binary search for sorted arrays)
            - Mathematical optimizations for number theory problems
            - Include necessary imports INSIDE the function if needed
            - Match exact function signature and return type
            """
        ]

        # Generate solutions in parallel
        solution_tasks = [
            self.generate(instruction=instr + f"\n\nBased on analysis:\n{problem_analysis}", context="")
            for instr in solution_instructions
        ]
        raw_solutions = await asyncio.gather(*solution_tasks)

        # Step 3: Ensemble Synthesis - Combine best elements or select optimal solution
        ensemble_instruction = f"""
        You are given three candidate solutions for the same programming problem.
        Your task is to synthesize the BEST possible solution by:
        1. Comparing correctness against problem requirements and edge cases identified in analysis: {problem_analysis}
        2. Evaluating code robustness (handles edge cases, type safety, no assumptions about input)
        3. Assessing efficiency and algorithmic soundness
        4. Ensuring exact function signature compliance and proper return types
        5. Preferring solutions that are both correct AND readable
        6. If one solution is clearly superior, select it. If elements from multiple solutions are needed, merge them intelligently.
        Output ONLY the final synthesized Python function implementation with necessary imports.
        """
        synthesized_solution = await self.ensemble(
            instruction=ensemble_instruction,
            contexts_list=raw_solutions
        )

        # Step 4: Iterative Refinement Loop (up to 2 iterations)
        current_solution = synthesized_solution
        for iteration in range(2):
            # Validate current solution
            validation_instruction = f"""
            Critically validate this solution against the original problem and analysis:
            Problem Analysis: {problem_analysis}
            
            Check for:
            - Logical errors or incorrect algorithmic approach
            - Missing edge case handling (empty inputs, boundaries, duplicates)
            - Type mismatches (returning list when tuple expected, etc.)
            - Efficiency issues (unnecessary loops, poor data structure choices)
            - Signature compliance (exact function name, parameter names, return type)
            - Proper import placement (inside function if needed)
            
            If no issues found, respond with "VALID: No issues detected".
            If issues found, describe them concisely and specifically.
            """
            validation_result = await self.generate(instruction=validation_instruction, context=current_solution)
            
            if "VALID:" in validation_result and "No issues detected" in validation_result:
                break  # Early termination if validated
            
            # Revise based on validation feedback
            revision_instruction = f"""
            Revise the solution to fix ALL issues identified in validation:
            Validation Feedback: {validation_result}
            
            Requirements:
            - Maintain exact function signature
            - Handle ALL edge cases from original analysis
            - Ensure type correctness and efficiency
            - Keep code clean and readable
            - Include necessary imports inside function if required
            """
            current_solution = await self.revise(instruction=revision_instruction, context=current_solution)

        # Step 5: Final Output Purification
        purification_instruction = """
        Extract ONLY the final Python function implementation from the text below.
        Requirements:
        - Must include exact function signature as specified in original problem
        - Must include any necessary imports (placed inside the function if needed)
        - Must be pure Python code with no markdown, explanations, or additional text
        - Must handle edge cases and match expected return types
        Output ONLY the code - nothing else.
        """
        final_code = await self.summarize(instruction=purification_instruction, context=current_solution)

        return final_code