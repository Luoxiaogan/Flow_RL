# Workflow ID: mbppplus_35_0
# Benchmark: mbppplus
# Data Indices: [110, 278, 21]

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
        import math

        # PHASE 1: Deep Problem Classification & Specification Extraction
        specification = await self.generate(
            instruction="""Perform deep structural analysis of this programming problem. Extract:
            1. EXACT input parameters and their types
            2. EXACT return type and format required
            3. Core algorithmic operation (e.g., product calculation, pattern matching, merging)
            4. Critical edge cases (empty inputs, single elements, boundaries, invalid values)
            5. Hidden constraints inferred from examples
            6. Required imports (re, math, etc.)
            7. Algorithmic complexity expectations if any
            Present as structured bullet points with explicit examples from test cases.""",
            context=""
        )

        # PHASE 2: Parallel Solution Generation (3 Diverse Strategies)
        solution_attempts = await asyncio.gather(
            self.generate(
                instruction=f"""Generate solution STRATEGY A: Literal Example-Driven Approach
                - Directly mimic patterns from provided test cases
                - Prioritize exact output format matching
                - Use simplest possible logic that satisfies examples
                - Explicitly handle edge cases mentioned in: {specification}
                Return ONLY the function implementation with necessary imports inside the function.""",
                context=specification
            ),
            self.generate(
                instruction=f"""Generate solution STRATEGY B: Formal Algorithmic Reconstruction
                - Derive mathematical/logical principles from problem description
                - Implement optimal algorithm (consider time/space complexity)
                - Include comprehensive edge case handling beyond examples
                - Ensure type consistency as specified in: {specification}
                Return ONLY the function implementation with necessary imports inside the function.""",
                context=specification
            ),
            self.generate(
                instruction=f"""Generate solution STRATEGY C: Defensive Programming Approach
                - Assume hostile inputs (invalid types, extreme values, empty cases)
                - Add input validation and graceful error handling
                - Over-engineer edge case coverage based on: {specification}
                - Prioritize robustness over elegance
                Return ONLY the function implementation with necessary imports inside the function.""",
                context=specification
            )
        )

        # PHASE 3: Parallel Validation of Each Solution
        validation_reports = await asyncio.gather(
            *[self.generate(
                instruction=f"""STATIC ANALYSIS VALIDATION for solution:
                {attempt}
                
                Check against specification: {specification}
                
                Validate:
                1. Return type matches exactly (int, bool, float, list, tuple, etc.)
                2. Handles all edge cases from specification
                3. No import missing for required modules
                4. Algorithm matches problem intent (not just examples)
                5. Potential failure modes (what inputs would break this?)
                Return bulleted list of vulnerabilities or 'PASSED' if flawless.""",
                context=attempt
            ) for attempt in solution_attempts]
        )

        # PHASE 4: Ensemble Synthesis - Merge Best Components
        final_solution = await self.ensemble(
            instruction=f"""Act as senior code reviewer. Synthesize final solution from these candidates:
            Candidate A: {solution_attempts[0]}
            Validation A: {validation_reports[0]}
            
            Candidate B: {solution_attempts[1]}
            Validation B: {validation_reports[1]}
            
            Candidate C: {solution_attempts[2]}
            Validation C: {validation_reports[2]}
            
            SYNTHESIS RULES:
            1. Take core algorithm from most mathematically sound candidate
            2. Take edge-case handling from most defensive candidate
            3. Take return-type precision from candidate with strictest type adherence
            4. Preserve variable names and structure from best core algorithm
            5. Inject any missing imports detected in validations
            6. Return ONLY the final function implementation - no explanations.
            
            If all candidates have critical flaws, create new synthesis addressing all vulnerabilities.""",
            contexts_list=solution_attempts
        )

        # PHASE 5: Iterative Refinement with Failure Simulation (up to 3 iterations)
        current_solution = final_solution
        for iteration in range(3):
            failure_simulation = await self.generate(
                instruction=f"""SIMULATE ADVERSARIAL TEST CASES for this solution:
                {current_solution}
                
                Based on specification: {specification}
                
                Generate 5 most likely failure scenarios:
                1. Extreme boundary values
                2. Empty/zero-length inputs
                3. Invalid data types
                4. Maximum/minimum possible inputs
                5. Cases that would cause logical errors or type mismatches
                
                For each, explain WHY it would fail and HOW to fix.
                If no vulnerabilities found, return 'ROBUST'.""",
                context=current_solution
            )
            
            if "ROBUST" in failure_simulation or "robust" in failure_simulation:
                break
                
            # Revise solution to handle simulated failures
            current_solution = await self.revise(
                instruction=f"""REVISE SOLUTION to handle these failure modes:
                {failure_simulation}
                
                Preserve core logic but add defensive checks, type handling, or edge case coverage.
                Maintain exact function signature and return type.
                Return ONLY the revised function implementation.""",
                context=current_solution
            )

        return current_solution