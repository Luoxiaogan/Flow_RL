# Workflow ID: mbppplus_23_0
# Benchmark: mbppplus
# Data Indices: [197, 20]

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

        # PHASE 1: Decompose & Classify
        decomposition_plan = await self.decompose(
            instruction="""Break this programming problem into atomic, solvable subproblems. For each subproblem, specify:
            1. Input type and structure (list, tuple, string, mixed, etc.)
            2. Expected output type and structure
            3. Core operation (sum, filter, transform, parse, etc.)
            4. Edge cases to handle (empty, single element, duplicates, type coercion, etc.)
            5. Any implicit constraints (order preservation, in-place modification, etc.)
            Return as structured subproblems with dependencies. Prioritize type and edge case identification first.""",
            context=""
        )

        # Extract critical metadata from decomposition
        classification = await self.generate(
            instruction=f"""Based on this decomposition:
            {decomposition_plan}
            
            Classify the problem into one of these categories:
            - Numeric Reduction (e.g., sum, product)
            - Conditional Transformation (e.g., increment numerics in mixed list)
            - String Parsing & Formatting
            - Data Structure Operation (set, dict, tuple manipulation)
            - Logic/Validation Problem
            
            Also extract:
            - Exact function name and signature
            - Required imports (if any)
            - Critical edge cases as bullet points
            - Expected return type (be explicit: list vs tuple vs scalar)
            
            Format as JSON-like structure for easy parsing.""",
            context=str(decomposition_plan)
        )

        # PHASE 2: Parallel Solution Generation & Validation
        # Generate 3 candidate solutions with different strategies
        candidate_instructions = [
            """Generate a solution prioritizing readability and explicit edge-case handling. 
            Use verbose variable names and comments. Include defensive checks for all edge cases identified.
            Structure: if/else guards for edge cases → main logic → return with explicit type casting.""",
            
            """Generate a solution prioritizing conciseness and Pythonic idioms (comprehensions, built-ins).
            Assume edge cases are handled elegantly through language features. 
            Avoid explicit conditionals unless absolutely necessary. Use type hints in comments.""",
            
            """Generate a solution prioritizing robustness and testability. 
            Write as if it will face 1000+ hidden test cases. Include assertions or try/except where appropriate.
            Handle type coercion explicitly. Document assumptions about input constraints."""
        ]

        candidate_solutions = await asyncio.gather(
            *[self.generate(instruction=instr, context=classification) for instr in candidate_instructions]
        )

        # Validate each candidate via code execution
        validation_tasks = []
        for i, candidate in enumerate(candidate_solutions):
            validation_task = self.programmer(
                instruction=f"""Execute this candidate solution against comprehensive test cases including:
                - Basic examples from problem
                - Edge cases: empty input, single element, extreme values, type mismatches
                - Performance stress test (large inputs)
                Return execution results, any errors, and pass/fail status.
                Candidate {i+1} context: {candidate}""",
                context=candidate,
                max_retries=1
            )
            validation_tasks.append(validation_task)
        
        validation_results = await asyncio.gather(*validation_tasks)

        # PHASE 3: Adversarial Revision & Synthesis
        # Revise each candidate by trying to break it
        revised_candidates = []
        for i, (candidate, validation) in enumerate(zip(candidate_solutions, validation_results)):
            revision = await self.revise(
                instruction=f"""Act as a ruthless QA engineer. Critique this solution:
                {candidate}
                
                Validation results: {validation}
                
                Find ALL weaknesses:
                - Unhandled edge cases
                - Type mismatches (e.g., returning list when tuple expected)
                - Logic errors in boundary conditions
                - Performance bottlenecks
                - Assumptions not stated in problem
                
                Then, revise the solution to fix EVERY identified issue. 
                Add explicit guards, type conversions, and edge-case handlers.
                Preserve the original approach but make it bulletproof.""",
                context=candidate
            )
            revised_candidates.append(revision)

        # Ensemble: Synthesize best elements into final solution
        final_solution = await self.ensemble(
            instruction="""Synthesize a final solution from these revised candidates:
            - Take the most robust edge-case handling from any candidate
            - Prefer the cleanest, most readable core logic
            - Ensure type consistency matches problem requirements
            - Eliminate any redundant or conflicting code
            - Output ONLY the final function implementation with necessary imports
            - Format exactly as required: no wrappers, exact function name, proper return types
            
            If candidates conflict on return type, prioritize the one matching problem's test cases.
            If multiple approaches are equally valid, choose the most efficient one.""",
            contexts_list=revised_candidates
        )

        # FINAL SANITY CHECK: Ensure output matches required format
        sanitized_solution = await self.revise(
            instruction="""Ensure this code meets EXACT output requirements:
            - Contains ONLY the function implementation (no extra text)
            - Uses exact function name from problem
            - Includes all necessary imports at top of function scope
            - Preserves function signature (parameter names, order)
            - Returns correct data type (list/tuple/set/scalar as required)
            - No outer classes or wrapper functions
            - Clean, PEP8-compliant formatting
            
            If any requirement is violated, fix it immediately.""",
            context=final_solution
        )

        return sanitized_solution