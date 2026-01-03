# Workflow ID: mbppplus_124_0
# Benchmark: mbppplus
# Data Indices: [187, 251]

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

        # PHASE 1: Problem Decomposition & Requirement Extraction
        decomposition = await self.generate(
            instruction="""Perform deep problem analysis. Extract:
            1. Exact function signature required (name, parameters, return type)
            2. Core transformation or computation needed
            3. Edge cases: empty inputs, single elements, boundary values, type variations
            4. Hidden constraints: order preservation, mutability, duplication handling
            5. Failure modes: what would make this solution break?
            6. Reference solution pitfalls (if any shown) - what's wrong with it?
            Format as structured bullet points with clear headers.""",
            context=""
        )

        # PHASE 2: Parallel Solution Generation (3 strategies)
        solution_attempts = await asyncio.gather(
            self.generate(
                instruction=f"""Generate Solution Strategy 1: DIRECT IMPLEMENTATION
                Based on decomposition:
                {decomposition}
                
                Write clean, minimal code that directly solves the problem.
                Prioritize readability and simplicity.
                Include type handling and basic edge cases.
                Return ONLY the function implementation as specified.""",
                context=decomposition
            ),
            self.generate(
                instruction=f"""Generate Solution Strategy 2: DEFENSIVE/EDGE-CASE FIRST
                Based on decomposition:
                {decomposition}
                
                Write code that explicitly handles ALL edge cases first:
                - Empty inputs
                - Single elements
                - Boundary values
                - Type mismatches
                - Mutability issues
                Structure code with guard clauses and explicit validations.
                Return ONLY the function implementation as specified.""",
                context=decomposition
            ),
            self.generate(
                instruction=f"""Generate Solution Strategy 3: REFERENCE-INSPIRED BUT CORRECTED
                Based on decomposition:
                {decomposition}
                
                If reference solution exists, identify its flaws and write corrected version.
                If no reference, write most robust possible implementation.
                Focus on correctness over elegance.
                Include comments explaining key decisions.
                Return ONLY the function implementation as specified.""",
                context=decomposition
            )
        )

        # PHASE 3: Parallel Validation & Revision
        validation_tasks = []
        for i, solution in enumerate(solution_attempts):
            validation = await self.generate(
                instruction=f"""CRITIQUE THIS SOLUTION:
                {solution}
                
                Based on problem decomposition:
                {decomposition}
                
                Identify:
                1. Edge cases this solution misses
                2. Type handling errors
                3. Logic flaws or off-by-one errors
                4. Performance or mutability issues
                5. Return type mismatches
                6. Any assumptions that could break in production
                Be brutally honest. List specific test cases that would fail.""",
                context=solution
            )
            validation_tasks.append(validation)

        # Revise each solution based on its validation
        revised_solutions = []
        for i, (solution, validation) in enumerate(zip(solution_attempts, validation_tasks)):
            revised = await self.revise(
                instruction=f"""REVISE THIS SOLUTION BASED ON CRITIQUE:
                Original solution:
                {solution}
                
                Critique:
                {validation}
                
                Requirements from decomposition:
                {decomposition}
                
                Fix all identified issues. Strengthen edge case handling.
                Ensure correct return types. Add necessary guards.
                Preserve function signature exactly.
                Return ONLY the corrected function implementation.""",
                context=solution
            )
            revised_solutions.append(revised)

        # PHASE 4: Ensemble Synthesis
        final_solution = await self.ensemble(
            instruction="""SYNTHESIZE THE BEST SOLUTION FROM ALL REVISIONS:
            You have multiple revised implementations. Create the optimal version by:
            1. Taking the most robust edge-case handling from any version
            2. Ensuring perfect type consistency and return format
            3. Preserving simplicity where possible
            4. Adding any missing validations or guards
            5. Ensuring no mutability issues or iteration pitfalls
            6. Matching EXACT function signature from original problem
            Prioritize correctness over elegance. Return ONLY the function implementation.""",
            contexts_list=revised_solutions
        )

        # PHASE 5: Final Safety Hardening
        hardened_solution = await self.revise(
            instruction=f"""FINAL SAFETY CHECK & HARDENING:
            Take this solution:
            {final_solution}
            
            And apply PARANOID hardening:
            1. Does it handle empty inputs? Test with [] or "" or None
            2. Does it handle single elements correctly?
            3. Are there any type assumptions that could break?
            4. Is there any iteration over mutable structure that could skip elements?
            5. Are return types EXACTLY as specified? (list vs tuple vs set)
            6. Are there any off-by-one errors or boundary condition misses?
            7. Would it break with negative numbers, zero, or extreme values?
            Fix ANY weaknesses found. Return ONLY the hardened function implementation.""",
            context=final_solution
        )

        return hardened_solution