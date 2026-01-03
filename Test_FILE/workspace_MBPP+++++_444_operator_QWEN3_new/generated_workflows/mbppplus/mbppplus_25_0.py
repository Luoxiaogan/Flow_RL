# Workflow ID: mbppplus_25_0
# Benchmark: mbppplus
# Data Indices: [280, 45, 169]

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

        # PHASE 1: STRUCTURED PROBLEM DECOMPOSITION
        problem_analysis = await self.generate(
            instruction="""Perform deep structural analysis of this programming problem. Extract:
            1. EXACT function signature (name, parameters, return type)
            2. Core algorithmic operation (what transformation is being performed?)
            3. Input constraints and edge cases (empty inputs, single elements, negatives, etc.)
            4. Output format requirements (must match test case return types exactly)
            5. Hidden constraints (order preservation, early termination, default values)
            6. Mathematical patterns or formulas that might apply
            Present as a structured JSON-like outline with clear section headers.""",
            context=""
        )

        # PHASE 2: PARALLEL SOLUTION GENERATION
        solution_attempts = await asyncio.gather(
            self.generate(
                instruction=f"""Generate Python implementation focusing on MATHEMATICAL ELEGANCE:
                - Use algebraic simplifications where possible
                - Prefer closed-form solutions over loops
                - Optimize for computational efficiency
                - Reference this analysis: {problem_analysis}
                Return ONLY the function code with necessary imports, nothing else.""",
                context=""
            ),
            self.generate(
                instruction=f"""Generate Python implementation focusing on ROBUSTNESS & EDGE CASES:
                - Handle all edge cases explicitly (empty inputs, single elements, etc.)
                - Use defensive programming with clear conditionals
                - Prioritize correctness over performance
                - Reference this analysis: {problem_analysis}
                Return ONLY the function code with necessary imports, nothing else.""",
                context=""
            ),
            self.generate(
                instruction=f"""Generate Python implementation focusing on LITERAL INTERPRETATION:
                - Follow problem description exactly as written
                - No optimizations or assumptions
                - Mimic reference solution style if available
                - Reference this analysis: {problem_analysis}
                Return ONLY the function code with necessary imports, nothing else.""",
                context=""
            )
        )

        # PHASE 3: SOLUTION SYNTHESIS
        synthesized_solution = await self.ensemble(
            instruction="""Synthesize the best solution from these candidates:
            1. Compare correctness against problem requirements
            2. Verify edge case handling completeness
            3. Check return type consistency with test cases
            4. Prefer solutions that match reference implementation patterns
            5. Combine strongest elements from each candidate if needed
            Return ONLY the final function code with necessary imports, nothing else.""",
            contexts_list=solution_attempts
        )

        # PHASE 4: EDGE CASE VALIDATION
        edge_cases = await self.generate(
            instruction=f"""Generate comprehensive edge case test scenarios based on:
            - Input types (lists, integers, etc.)
            - Boundary conditions (empty, single element, extremes)
            - Special values (zero, negatives, duplicates)
            - Type mismatches
            Format as Python assert statements that should pass with correct implementation.
            Reference problem analysis: {problem_analysis}""",
            context=""
        )

        # PHASE 5: ITERATIVE REFINEMENT
        current_solution = synthesized_solution
        for iteration in range(3):
            validation_feedback = await self.generate(
                instruction=f"""Rigorously validate this solution against problem requirements:
                1. Does it handle all edge cases from: {edge_cases}?
                2. Does return type match expected outputs?
                3. Are there any logical flaws or off-by-one errors?
                4. Is the implementation unnecessarily complex?
                5. Does it match the algorithmic pattern identified in analysis?
                If issues found, describe them specifically. If perfect, say 'VALIDATED'.""",
                context=current_solution
            )
            
            if "VALIDATED" in validation_feedback.upper():
                break
                
            current_solution = await self.revise(
                instruction=f"""Fix all issues identified in validation:
                Validation feedback: {validation_feedback}
                Problem analysis: {problem_analysis}
                Edge cases: {edge_cases}
                Return ONLY the corrected function code with necessary imports, nothing else.""",
                context=current_solution
            )

        # PHASE 6: FINAL TYPE & FORMAT SANITIZATION
        final_solution = await self.revise(
            instruction="""Ensure absolute compliance with output requirements:
            1. Function name must exactly match specification
            2. Return type must match test case expectations (list vs tuple vs int)
            3. No extra print statements or debug code
            4. All necessary imports included at top
            5. Code must be self-contained (no external dependencies)
            Return ONLY the final function code with necessary imports, nothing else.""",
            context=current_solution
        )

        return final_solution