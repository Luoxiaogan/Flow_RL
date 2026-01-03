# Workflow ID: mbppplus_4_0
# Benchmark: mbppplus
# Data Indices: [346, 82, 201]

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

        # PHASE 1: PARALLEL HYPOTHESIS GENERATION
        # Generate three independent solution attempts from different reasoning perspectives
        perspectives = await asyncio.gather(
            self.generate(
                instruction="""You are a mathematical logic expert. Analyze the problem through a formal, mathematical lens:
                - Identify numerical invariants, algebraic relationships, or logical constraints
                - Express the solution as a precise algorithm with minimal state
                - Consider edge cases: empty inputs, single elements, zeros, negatives
                - Return ONLY the function implementation with correct signature and imports
                - Ensure return type matches expected output (list/tuple/set/bool/int)
                - Use efficient loops and early returns where possible
                - Add brief inline comments for non-obvious logic steps""",
                context=""
            ),
            self.generate(
                instruction="""You are a systems architect. Analyze the problem through a structural, algorithmic lens:
                - Identify data flow, iteration patterns, and state transitions
                - Consider time/space complexity trade-offs
                - Handle boundary conditions explicitly
                - Return ONLY the function implementation with correct signature and imports
                - Match exact parameter names and return types
                - Use descriptive variable names and clear control flow
                - Include defensive checks for invalid inputs if implied by tests""",
                context=""
            ),
            self.generate(
                instruction="""You are a semantic analyst. Analyze the problem through a linguistic, pattern-matching lens:
                - Extract keywords and implied operations from problem description
                - Map to known algorithmic patterns (search, filter, transform, validate)
                - Infer test case behavior even if not explicitly shown
                - Return ONLY the function implementation with correct signature and imports
                - Preserve order if tests imply it matters
                - Handle duplicates, case sensitivity, type conversions as needed
                - Comment on any assumptions made about input constraints""",
                context=""
            )
        )

        # PHASE 2: PARALLEL REVISION AGAINST IMPLICIT TESTS
        # Revise each solution by simulating test case behavior
        revised_solutions = await asyncio.gather(
            *[self.revise(
                instruction=f"""Critically evaluate this solution against the problem's implied test cases:
                - Mentally execute against provided examples (even if not shown, infer from signature)
                - Check for type mismatches (list vs tuple, int vs bool)
                - Verify edge case handling: empty inputs, single elements, duplicates
                - Ensure algorithmic correctness for boundary values
                - Fix any logical errors or off-by-one mistakes
                - Optimize for clarity and efficiency without changing behavior
                - Return ONLY the corrected function implementation""",
                context=sol
            ) for sol in perspectives]
        )

        # PHASE 3: SYNTHESIZE BEST SOLUTION
        # Ensemble doesn't just pick - it synthesizes a new solution combining strengths
        synthesized = await self.ensemble(
            instruction="""Synthesize a final solution by combining the strongest elements from all candidates:
            - Take correct mathematical logic from any source
            - Adopt clearest control flow and variable naming
            - Incorporate most comprehensive edge case handling
            - Ensure perfect signature and return type compliance
            - Eliminate redundant operations or unnecessary complexity
            - Add minimal comments only for non-obvious logic
            - Return ONLY the final function implementation with imports""",
            contexts_list=revised_solutions
        )

        # PHASE 4: ITERATIVE VALIDATION LOOP (up to 3 rounds)
        current_solution = synthesized
        for validation_round in range(3):
            validation = await self.generate(
                instruction=f"""Simulate test execution of this code:
                - Mentally run against all implied test cases from problem description
                - Check return values, types, and side effects
                - Identify any discrepancies or edge case failures
                - If perfect, respond with 'VALIDATED'
                - If issues found, describe them concisely and suggest fixes""",
                context=current_solution
            )
            
            if "VALIDATED" in validation.upper():
                break
                
            # Revise based on validation feedback
            current_solution = await self.revise(
                instruction=f"""Fix all issues identified in validation:
                Validation feedback: {validation}
                - Address every point raised
                - Maintain correct function signature
                - Preserve working parts of existing solution
                - Return ONLY the corrected function implementation""",
                context=current_solution
            )
        else:
            # If we exhausted all rounds, use last revision
            pass

        return current_solution