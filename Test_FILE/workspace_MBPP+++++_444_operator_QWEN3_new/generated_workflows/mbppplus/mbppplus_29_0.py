# Workflow ID: mbppplus_29_0
# Benchmark: mbppplus
# Data Indices: [175, 368, 221]

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

        # Step 1: Generate three parallel problem interpretations
        interpretation_instructions = [
            """Analyze the problem with focus on DATA STRUCTURES and TYPE CONTRACTS:
            - What are the exact input types? (list, tuple, string, etc.)
            - What is the required output type and format?
            - Are there mutability or immutability constraints?
            - What type conversions are implied or forbidden?
            Structure your response as a bullet-point specification.""",
            
            """Analyze the problem with focus on LOGICAL CONDITIONS and ALGORITHMIC STEPS:
            - What are the core logical rules or mathematical operations?
            - What sequence of steps solves the problem?
            - Are there conditional branches or loops required?
            - What constitutes success vs failure?
            Structure your response as a numbered procedure.""",
            
            """Analyze the problem with focus on EDGE CASES and BOUNDARY CONDITIONS:
            - What are the minimal/empty/degenerate inputs?
            - What are the maximum/overflow/invalid inputs?
            - What are the corner cases that might break naive solutions?
            - How should errors or invalid inputs be handled?
            Structure your response as a test case inventory."""
        ]

        interpretations = await asyncio.gather(
            *[self.generate(instr, "") for instr in interpretation_instructions]
        )

        # Step 2: Ensemble interpretations into a unified spec
        unified_spec = await self.ensemble(
            instruction="""Reconcile these three problem interpretations into a single, unambiguous specification.
            Resolve conflicts by:
            1. Prioritizing explicit constraints from the problem text
            2. Favoring stricter interpretations over lenient ones
            3. Preserving all edge cases mentioned in any interpretation
            4. Maintaining exact type and format requirements
            Output a comprehensive spec covering: input/output types, core logic, edge cases, and constraints.""",
            contexts_list=interpretations
        )

        # Step 3: Generate three parallel solution attempts
        solution_instructions = [
            """Implement the solution with focus on MINIMALISM and CLARITY:
            - Use the simplest possible logic that satisfies the spec
            - Prioritize readability over cleverness
            - Use descriptive variable names
            - Include no unnecessary checks or optimizations
            Return ONLY the function implementation as specified.""",
            
            """Implement the solution with focus on ROBUSTNESS and EDGE CASES:
            - Explicitly handle every edge case in the spec
            - Add defensive checks for invalid inputs
            - Include comments for complex logic
            - Prioritize correctness over elegance
            Return ONLY the function implementation as specified.""",
            
            """Implement the solution with focus on PERFORMANCE and IDIOMATIC PYTHON:
            - Use the most efficient algorithms and data structures
            - Leverage Python built-ins and standard library
            - Avoid unnecessary loops or allocations
            - Write idiomatic, Pythonic code
            Return ONLY the function implementation as specified."""
        ]

        solution_attempts = await asyncio.gather(
            *[self.generate(instr, unified_spec) for instr in solution_instructions]
        )

        # Step 4: Critique each solution against the unified spec
        critique_instructions = [
            f"""Critique this solution against the unified specification:
            SPECIFICATION:
            {unified_spec}
            
            SOLUTION:
            {attempt}
            
            Identify:
            1. Any deviation from required input/output types
            2. Missing edge case handling
            3. Logical errors or incorrect algorithm
            4. Format violations (wrong function name, extra wrappers, etc.)
            5. Unnecessary complexity or inefficiency
            Be brutally honest. If the solution is fundamentally flawed, say so.
            Format as a bullet-point list of violations, severity (critical/major/minor), and suggested fixes."""
            for attempt in solution_attempts
        ]

        critiques = await asyncio.gather(
            *[self.revise(instr, attempt) for instr, attempt in zip(critique_instructions, solution_attempts)]
        )

        # Step 5: Ensemble to select and annotate the best solution
        selected_solution_info = await self.ensemble(
            instruction="""Select the best solution from the three attempts based on:
            1. Fewest critical violations (type mismatches, logic errors)
            2. Fewest major violations (missing edge cases)
            3. Cleanest code structure
            Output format:
            SELECTED: [index 0, 1, or 2]
            FIXES REQUIRED: [concise list of required changes]
            RATIONALE: [brief justification]""",
            contexts_list=[f"Solution {i}:\n{sol}\n\nCritique:\n{crit}" 
                          for i, (sol, crit) in enumerate(zip(solution_attempts, critiques))]
        )

        # Parse selection (simple extraction since format is controlled)
        selected_index = 0
        if "SELECTED: 1" in selected_solution_info:
            selected_index = 1
        elif "SELECTED: 2" in selected_solution_info:
            selected_index = 2

        # Step 6: Apply fixes to selected solution
        fix_instruction = f"""Apply these fixes to the solution:
        {selected_solution_info}
        
        Original solution:
        {solution_attempts[selected_index]}
        
        Instructions:
        1. Make ONLY the changes required to fix violations
        2. Preserve all correct behavior
        3. Maintain exact function signature and return type
        4. Do not add new features or optimizations
        Return ONLY the corrected function implementation."""
        
        fixed_solution = await self.revise(fix_instruction, solution_attempts[selected_index])

        # Step 7: Final cleanup and format enforcement
        final_solution = await self.summarize(
            instruction="""Clean and standardize this code:
            - Ensure EXACT function name and parameter names as in problem
            - Remove any debug prints, extra comments, or wrapper code
            - Format to PEP8 standards (but preserve logic)
            - Return ONLY the function implementation with necessary imports
            - Imports must be inside the function if required
            The output must be ready for direct execution and testing.""",
            context=fixed_solution
        )

        return final_solution