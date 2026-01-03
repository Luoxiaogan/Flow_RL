# Workflow ID: mbppplus_9_0
# Benchmark: mbppplus
# Data Indices: [87, 4]

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

        # PHASE 1: PROBLEM CLASSIFICATION & STRATEGY SELECTION
        classification = await self.generate(
            instruction="""Perform deep problem classification. Analyze the function signature and description to determine:
            1. Primary domain: Mathematical, Logical, String, Data Structure, or Algorithmic?
            2. Key operations needed: Arithmetic, Iteration, Recursion, Set operations, String parsing, etc.
            3. Critical edge cases: Empty inputs, zero, negatives, duplicates, type boundaries, overflow conditions.
            4. Expected return type: Must match exactly (list vs tuple vs set vs float vs bool).
            5. Known algorithms or formulas that apply (e.g., Pythagorean theorem, Sieve of Eratosthenes).
            6. Potential failure points: Type errors, infinite loops, precision loss, off-by-one errors.
            Output structured analysis with clear sections for each point above.""",
            context=""
        )

        # PHASE 2: PARALLEL SOLUTION GENERATION (DIAMOND PATTERN)
        solution_attempts = await asyncio.gather(
            self.generate(
                instruction=f"""Generate Solution Attempt 1 (Mathematical/Formulaic Approach):
                Based on classification: {classification}
                - Use known mathematical identities or library functions where appropriate.
                - Prioritize precision and correctness over performance.
                - Include type annotations and explicit return type casting.
                - Handle edge cases identified in classification.
                Output ONLY the function implementation with imports, no explanations.""",
                context=""
            ),
            self.generate(
                instruction=f"""Generate Solution Attempt 2 (Algorithmic/Step-by-Step Approach):
                Based on classification: {classification}
                - Implement from first principles, no external libraries unless necessary.
                - Show clear, commented logic for each step.
                - Explicitly handle all edge cases from classification.
                - Ensure return type matches exactly.
                Output ONLY the function implementation with imports, no explanations.""",
                context=""
            ),
            self.generate(
                instruction=f"""Generate Solution Attempt 3 (Defensive/Edge-Case First Approach):
                Based on classification: {classification}
                - Start by handling all edge cases explicitly at function start.
                - Use guard clauses and early returns for invalid inputs.
                - Validate input types and ranges before computation.
                - Prioritize robustness over elegance.
                Output ONLY the function implementation with imports, no explanations.""",
                context=""
            )
        )

        # PHASE 3: SYNTHESIZE BEST SOLUTION VIA ENSEMBLE
        synthesized_solution = await self.ensemble(
            instruction="""Synthesize a final solution from the three attempts:
            - Compare logic, edge case handling, and return type consistency.
            - Prefer mathematical precision where applicable, but prioritize correctness.
            - Merge robust edge-case handling from defensive approach.
            - Ensure clean, readable code with necessary comments.
            - MUST preserve exact function signature and return type.
            - If conflicts exist, choose the most conservative (safest) implementation.
            Output ONLY the final function implementation with imports, no explanations.""",
            contexts_list=solution_attempts
        )

        # PHASE 4: VALIDATION & REFINEMENT LOOP (MAX 2 ITERATIONS)
        current_solution = synthesized_solution
        for iteration in range(2):
            validation_result = await self.programmer(
                instruction=f"""Validate this implementation against comprehensive test cases:
                Based on classification: {classification}
                Generate and run tests for:
                - All edge cases mentioned in classification
                - Boundary values (min/max, zero, negatives, empty)
                - Type consistency (ensure return type matches exactly)
                - Performance on large inputs (if applicable)
                - Precision requirements (if floating point)
                Return detailed error log if any test fails, otherwise return 'PASSED'.""",
                context=current_solution,
                max_retries=1
            )

            if "PASSED" in validation_result:
                break
            else:
                # REVISE BASED ON ERRORS
                current_solution = await self.revise(
                    instruction=f"""REVISE FUNCTION BASED ON VALIDATION ERRORS:
                    Validation failed with: {validation_result}
                    Classification context: {classification}
                    - Diagnose root cause: logic error, edge case missed, type mismatch, precision issue?
                    - Fix ONLY the failing cases while preserving existing correct behavior.
                    - Add inline comments explaining the fix.
                    - Re-verify return type and signature.
                    Output ONLY the revised function implementation with imports.""",
                    context=current_solution
                )
        else:
            # FALLBACK: DECOMPOSE AND REBUILD IF STILL FAILING
            decomposition = await self.decompose(
                instruction="""Decompose into atomic subproblems:
                1. Input validation and type checking
                2. Core computation logic
                3. Edge case handling
                4. Return value formatting and type casting
                Treat each as independent subproblem with clear dependencies.""",
                context=""
            )
            
            # SOLVE EACH SUBPROBLEM INDEPENDENTLY
            sub_solutions = {}
            for sub in decomposition:
                sub_sol = await self.generate(
                    instruction=f"""Solve subproblem: {sub['description']}
                    Classification context: {classification}
                    Dependencies (if any): {sub.get('dependencies', '')}
                    Output ONLY the code snippet for this subproblem, no explanations.""",
                    context=""
                )
                sub_solutions[sub['id']] = sub_sol
            
            # REASSEMBLE (SIMPLIFIED - IN PRACTICE WOULD NEED DEPENDENCY RESOLUTION)
            reassembled = await self.generate(
                instruction=f"""Reassemble final solution from subproblem solutions:
                Subproblem solutions: {sub_solutions}
                Classification: {classification}
                - Integrate snippets into complete function
                - Ensure proper flow and variable naming
                - Add necessary imports
                - Verify signature and return type
                Output ONLY final function implementation with imports.""",
                context=""
            )
            current_solution = reassembled

        # FINAL SANITY CHECK
        final_check = await self.summarize(
            instruction="""Final verification:
            - Does this code exactly match the required function signature?
            - Are all edge cases from classification handled?
            - Is return type correct and consistent?
            - Are there any obvious logic errors or anti-patterns?
            If any issue, return 'REJECT: [reason]'. Otherwise return 'ACCEPT'.""",
            context=current_solution
        )

        if "REJECT" in final_check:
            # LAST RESORT: RETURN MOST DEFENSIVE ORIGINAL ATTEMPT
            current_solution = solution_attempts[2]  # Defensive approach

        return current_solution