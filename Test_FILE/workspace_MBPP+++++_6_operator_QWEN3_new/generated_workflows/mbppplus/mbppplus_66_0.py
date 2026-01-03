# Workflow ID: mbppplus_66_0
# Benchmark: mbppplus
# Data Indices: [316, 259]

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

        # STEP 1: CLASSIFY THE PROBLEM TYPE AND EXTRACT KEY CONSTRAINTS
        classification = await self.generate(
            instruction="""Perform a deep structural analysis of this programming problem. Your analysis must include:
            1. Problem Category: Classify as one of: string_pattern, list_operation, mathematical_computation, data_structure_algorithm, logic_validation, or other.
            2. Input/Output Specification: What are the expected input types and output types? Be specific (e.g., "list of integers", "string", "boolean").
            3. Key Operations: What core operations are required? (e.g., "find intersection", "validate pattern", "compute factorial")
            4. Edge Cases: List all potential edge cases mentioned or implied (e.g., empty input, single element, duplicates, negative numbers).
            5. Constraints: Any explicit or implicit constraints (e.g., "must preserve order", "no external libraries", "time complexity").
            6. Confidence Level: How confident are you in this classification? (High/Medium/Low)
            Format your response as a structured JSON-like block with these keys.""",
            context=""
        )

        # STEP 2: GENERATE MULTIPLE SOLUTION STRATEGIES IN PARALLEL
        strategy_instructions = [
            """Based on the problem classification, develop a REGEX-BASED solution strategy. 
            Focus on pattern matching, string validation, or text extraction. 
            Describe the regex pattern(s) needed, flags, and how to handle edge cases. 
            Include example matches and non-matches if applicable.""",
            
            """Based on the problem classification, develop an ALGORITHMIC solution strategy.
            Focus on loops, conditionals, recursion, or mathematical formulas.
            Describe step-by-step logic, data structures used, and complexity considerations.
            Include pseudocode if helpful.""",
            
            """Based on the problem classification, develop a SET/LIST OPERATION solution strategy.
            Focus on built-in Python operations like set intersection, list comprehensions, filtering.
            Describe transformations, type conversions, and order preservation needs.
            Include handling of duplicates and empty cases."""
        ]

        strategy_contexts = await asyncio.gather(
            *[self.generate(instruction=instr, context=classification) for instr in strategy_instructions]
        )

        # STEP 3: CONVERT STRATEGIES TO EXECUTABLE CODE (PARALLEL)
        code_attempts = []
        for i, strategy in enumerate(strategy_contexts):
            try:
                code = await self.programmer(
                    instruction=f"""Convert this solution strategy into a Python function that solves the original problem.
                    STRICT REQUIREMENTS:
                    - Use the EXACT function name and signature from the problem.
                    - Include ONLY necessary imports inside the function if needed.
                    - Return the EXACT expected data type (match test cases).
                    - Handle ALL edge cases mentioned in classification.
                    - Code must be clean, efficient, and readable.
                    - Output ONLY the function implementation - no explanations, no wrappers.
                    
                    Strategy to implement:
                    {strategy}""",
                    context=strategy,
                    max_retries=3
                )
                # Validate code format
                if "def " in code and not code.startswith("Error"):
                    code_attempts.append(code)
            except Exception:
                continue

        # STEP 4: VALIDATE AND REVISE CODE ATTEMPTS (PARALLEL)
        validated_codes = []
        for code in code_attempts:
            try:
                revised = await self.revise(
                    instruction="""Critically review this code solution:
                    1. Does it handle ALL edge cases (empty input, single element, duplicates, type mismatches)?
                    2. Does it match the expected output type and format?
                    3. Is the logic correct and efficient?
                    4. Are variable names clear and consistent?
                    5. Are imports properly placed (inside function if needed)?
                    6. Does it follow the exact function signature?
                    If any issues found, fix them. Return ONLY the corrected function implementation.""",
                    context=code
                )
                if "def " in revised and not revised.startswith("Error"):
                    validated_codes.append(revised)
            except Exception:
                continue

        # STEP 5: ENSEMBLE - SELECT BEST SOLUTION
        if len(validated_codes) > 1:
            final_code = await self.ensemble(
                instruction="""Select the BEST solution from these candidates:
                Criteria (in order of priority):
                1. Correctness: Handles all edge cases and matches expected output type.
                2. Robustness: Most defensive programming, best error handling.
                3. Efficiency: Most optimal time/space complexity.
                4. Readability: Cleanest code, best variable names.
                5. Simplicity: Fewest unnecessary operations.
                Return ONLY the selected function implementation - no explanations.""",
                contexts_list=validated_codes
            )
        elif len(validated_codes) == 1:
            final_code = validated_codes[0]
        else:
            # FALLBACK: Use decomposition for complex problems
            try:
                subproblems = await self.decompose(
                    instruction="""Break this problem into minimal independent subproblems.
                    Each subproblem should be solvable in isolation.
                    Return list of subproblems with dependencies.""",
                    context=classification
                )
                
                # Solve subproblems (simplified - in practice would need dependency resolution)
                sub_solutions = []
                for sp in subproblems:
                    sub_sol = await self.programmer(
                        instruction=f"""Solve this subproblem: {sp['description']}
                        Return ONLY the function or code snippet needed.""",
                        context="",
                        max_retries=2
                    )
                    sub_solutions.append(sub_sol)
                
                # Synthesize final solution
                final_code = await self.generate(
                    instruction=f"""Combine these subproblem solutions into a complete answer:
                    Subproblems: {sub_solutions}
                    Ensure final output matches original problem's function signature and requirements.
                    Return ONLY the final function implementation.""",
                    context=str(sub_solutions)
                )
            except Exception:
                # Ultimate fallback - return simplest possible solution
                final_code = await self.programmer(
                    instruction="""Generate the simplest possible correct solution.
                    Focus on core functionality first, then add edge case handling.
                    Return ONLY the function implementation.""",
                    context=classification,
                    max_retries=3
                )

        return final_code