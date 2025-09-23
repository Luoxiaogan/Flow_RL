# Workflow ID: mbppplus_46_0
# Benchmark: mbppplus
# Data Indices: [363, 355, 117]

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
        import json

        # PHASE 1: PARALLEL PROBLEM INTERPRETATION
        interpretation_tasks = [
            self.generate(
                instruction="""Analyze the problem from a TYPE CONTRACT perspective:
                - What are the exact input types? (str, list, tuple, etc.)
                - What is the required output type? (must match test assertions exactly)
                - Are there any implicit type conversions needed?
                - Document any type-related constraints or edge cases.
                Format as structured JSON with keys: input_type, output_type, constraints.""",
                context=""
            ),
            self.generate(
                instruction="""Analyze the problem from an EDGE CASE perspective:
                - What are the boundary conditions? (empty inputs, single elements, max/min values)
                - What are the failure modes? (type mismatches, index errors, division by zero)
                - What special values need handling? (None, 0, negative numbers, whitespace)
                - List at least 5 specific edge cases that must be handled.
                Format as numbered list with brief explanations.""",
                context=""
            ),
            self.generate(
                instruction="""Analyze the problem from an ALGORITHMIC PATTERN perspective:
                - What category does this problem belong to? (filtering, mapping, reducing, searching, etc.)
                - What Python constructs are most suitable? (list comprehensions, slicing, regex, built-ins)
                - Are there standard library functions that could solve this directly?
                - What is the time/space complexity requirement?
                Format as bullet points with clear categorization.""",
                context=""
            )
        ]
        
        interpretations = await asyncio.gather(*interpretation_tasks)
        
        # Synthesize interpretations into unified spec
        problem_spec = await self.ensemble(
            instruction="""Synthesize the three analyses into a single, comprehensive problem specification:
            1. Combine type contracts, edge cases, and algorithmic patterns into a coherent whole.
            2. Resolve any conflicts between interpretations (default to most conservative/robust approach).
            3. Explicitly state the expected function signature and return type.
            4. List all edge cases that must be handled.
            5. Recommend the most appropriate algorithmic approach.
            Format as structured document with clear sections.""",
            contexts_list=interpretations
        )

        # PHASE 2: PARALLEL SOLUTION GENERATION
        solution_tasks = [
            self.generate(
                instruction=f"""Generate a MINIMALISTIC solution:
                Problem Spec: {problem_spec}
                
                Requirements:
                - Use the simplest possible logic that satisfies the core requirement.
                - Prioritize brevity and directness over robustness.
                - Do NOT handle edge cases unless absolutely necessary for basic functionality.
                - Return exactly the required type (list, tuple, etc.) as specified.
                - Include brief comments explaining the core logic.
                
                IMPORTANT: The solution must be a complete, runnable Python function with the exact name specified in the problem.""",
                context=problem_spec
            ),
            self.generate(
                instruction=f"""Generate a ROBUST solution:
                Problem Spec: {problem_spec}
                
                Requirements:
                - Explicitly handle ALL edge cases identified in the specification.
                - Include defensive programming (type checks, boundary checks).
                - Use clear, verbose variable names and comprehensive comments.
                - Structure code to be easily maintainable and debuggable.
                - Return exactly the required type (list, tuple, etc.) as specified.
                
                IMPORTANT: The solution must be a complete, runnable Python function with the exact name specified in the problem.""",
                context=problem_spec
            ),
            self.generate(
                instruction=f"""Generate an IDIOMATIC solution:
                Problem Spec: {problem_spec}
                
                Requirements:
                - Use Python's most idiomatic constructs (list comprehensions, slicing, built-ins, etc.)
                - Leverage standard library functions where appropriate.
                - Prioritize Pythonic style and efficiency.
                - Keep code concise but readable.
                - Return exactly the required type (list, tuple, etc.) as specified.
                
                IMPORTANT: The solution must be a complete, runnable Python function with the exact name specified in the problem.""",
                context=problem_spec
            )
        ]
        
        solutions = await asyncio.gather(*solution_tasks)

        # PHASE 3: SOLUTION VALIDATION AND SELECTION
        validation_tasks = [
            self.generate(
                instruction=f"""Validate this solution against the problem specification:
                Problem Spec: {problem_spec}
                Solution: {solution}
                
                Check for:
                1. Type correctness (input handling and return type)
                2. Edge case coverage (all specified edge cases must be handled)
                3. Logical correctness (does it solve the core problem?)
                4. Code quality (readability, efficiency, Pythonic style)
                
                Return "VALID" if all checks pass, otherwise return detailed error report.
                Be strict - if any requirement is not met, it's invalid.""",
                context=solution
            ) for solution in solutions
        ]
        
        validations = await asyncio.gather(*validation_tasks)
        
        # Filter valid solutions
        valid_solutions = [sol for sol, val in zip(solutions, validations) if "VALID" in val.upper()]
        
        if not valid_solutions:
            # If no solution is valid, use the most robust one and flag for revision
            selected_solution = solutions[1]  # Robust solution as fallback
            needs_revision = True
        else:
            # Ensemble valid solutions
            if len(valid_solutions) == 1:
                selected_solution = valid_solutions[0]
            else:
                selected_solution = await self.ensemble(
                    instruction="""Select the best solution from the valid candidates:
                    Criteria (in order of priority):
                    1. Most comprehensive edge case handling
                    2. Cleanest, most readable code
                    3. Most efficient/time-complexity optimal
                    4. Most Pythonic/idiomatic
                    
                    If solutions are equally good, prefer the more concise one.
                    Return the complete selected solution as is - do not modify it.""",
                    contexts_list=valid_solutions
                )
            needs_revision = False

        # PHASE 4: ITERATIVE REFINEMENT (if needed)
        current_solution = selected_solution
        
        if needs_revision:
            # First revision: Fix critical issues
            current_solution = await self.revise(
                instruction=f"""Revise this solution to fix validation failures:
                Problem Spec: {problem_spec}
                Validation Report: {validations[1]}  # Using robust solution's validation
                
                Requirements:
                - Fix all type mismatches (ensure exact return type)
                - Add missing edge case handling
                - Correct any logical errors
                - Maintain the original solution's core approach
                - Return complete, runnable function with exact name specified""",
                context=current_solution
            )
        
        # Second revision: Ensure type conformance and edge case hardening
        current_solution = await self.revise(
            instruction=f"""Revise for TYPE CONFORMANCE and EDGE CASE HARDENING:
            Problem Spec: {problem_spec}
            
            Requirements:
            - Verify return type matches specification EXACTLY (list vs tuple vs set)
            - Add explicit handling for empty inputs, single elements, and boundary cases
            - Include type assertions or checks if appropriate
            - Ensure no index errors or type conversion errors possible
            - Keep code as clean and efficient as possible
            - Return complete, runnable function with exact name specified""",
            context=current_solution
        )
        
        # Third revision: Optimize for clarity and efficiency
        final_solution = await self.revise(
            instruction=f"""Final polish for CLARITY and EFFICIENCY:
            Problem Spec: {problem_spec}
            
            Requirements:
            - Use most efficient Python constructs (slicing instead of loops where possible)
            - Remove any redundant code or unnecessary variables
            - Ensure variable names are clear and meaningful
            - Add brief comments only where logic is non-obvious
            - Verify solution is as concise as possible without sacrificing readability
            - Return complete, runnable function with exact name specified""",
            context=current_solution
        )

        return final_solution