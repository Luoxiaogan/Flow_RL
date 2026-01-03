# Workflow ID: humaneval_38_0
# Benchmark: humaneval
# Data Indices: [42, 26]

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

        # PHASE 1: Deep problem analysis and pattern extraction
        problem_analysis = await self.generate(
            instruction="""Perform a forensic analysis of the function specification:
            1. Extract all input-output examples from the docstring. Format them as structured pairs.
            2. Infer the transformation rule from these examples. Is it mathematical? Logical? Structural?
            3. Identify the expected input and output types. Are they lists? strings? integers? Be precise.
            4. Predict edge cases not shown in examples (empty inputs, single elements, boundary values).
            5. Note any ordering, mutability, or side-effect constraints implied by the examples.
            6. Summarize the core algorithm in plain English, as if explaining to another programmer.
            Be exhaustive. Your analysis will drive the entire solution process.""",
            context=""
        )

        # PHASE 2: Generate multiple candidate solutions in parallel (Diamond Pattern)
        candidate_tasks = [
            self.generate(
                instruction=f"""Generate a Python function implementation using a LIST COMPREHENSION approach.
                Problem Analysis: {problem_analysis}
                Guidelines:
                - Use list comprehensions or generator expressions where possible.
                - Prioritize readability and Pythonic style.
                - Handle edge cases predicted in the analysis.
                - Match return types exactly as shown in examples (int vs float, list vs tuple).
                - Function name must match ENTRY POINT exactly.
                - Return only the function body, no imports or explanations.""",
                context=problem_analysis
            ),
            self.generate(
                instruction=f"""Generate a Python function implementation using an IMPERATIVE LOOP approach.
                Problem Analysis: {problem_analysis}
                Guidelines:
                - Use explicit for/while loops and mutable state.
                - Prioritize clarity of step-by-step logic.
                - Handle edge cases predicted in the analysis.
                - Match return types exactly as shown in examples.
                - Function name must match ENTRY POINT exactly.
                - Return only the function body, no imports or explanations.""",
                context=problem_analysis
            ),
            self.generate(
                instruction=f"""Generate a Python function implementation using a FUNCTIONAL PROGRAMMING approach.
                Problem Analysis: {problem_analysis}
                Guidelines:
                - Use map, filter, reduce, or itertools where appropriate.
                - Avoid explicit loops; prefer higher-order functions.
                - Handle edge cases predicted in the analysis.
                - Match return types exactly as shown in examples.
                - Function name must match ENTRY POINT exactly.
                - Return only the function body, no imports or explanations.""",
                context=problem_analysis
            )
        ]
        
        candidate_solutions = await asyncio.gather(*candidate_tasks)

        # PHASE 3: Self-critique and edge case hardening for each candidate
        revised_candidates = []
        for i, candidate in enumerate(candidate_solutions):
            revised = await self.revise(
                instruction=f"""Critically revise this solution:
                1. Simulate edge cases: empty input, single element, extreme values, type boundaries.
                2. Verify type consistency: if examples return int, NEVER return float. If list, NEVER tuple.
                3. Check for off-by-one errors, index errors, or logical gaps.
                4. Ensure no over-engineering: implement ONLY what's specified.
                5. If flaws are found, revise the code. If not, return it unchanged.
                Be ruthless. Hidden test cases will fail on any imperfection.""",
                context=candidate
            )
            revised_candidates.append(revised)

        # PHASE 4: Ensemble synthesis with validation-focused selection
        final_solution = await self.ensemble(
            instruction="""Select or synthesize the best solution using these criteria:
            1. TYPE CORRECTNESS: Must match example return types exactly (int/float, list/tuple, etc.).
            2. EDGE CASE COVERAGE: Must handle empty inputs, single elements, and boundary conditions.
            3. SIMPLICITY: Prefer the most straightforward implementation that meets requirements.
            4. EXAMPLE ALIGNMENT: Must perfectly reproduce all shown input-output pairs.
            5. If multiple solutions are equally valid, SYNTHESIZE a hybrid that combines their strengths.
            Return ONLY the final function body. No explanations, no imports, no markdown.""",
            contexts_list=revised_candidates
        )

        # PHASE 5: Final type and signature enforcement
        polished_solution = await self.revise(
            instruction="""Final polish:
            1. Verify function name matches ENTRY POINT exactly.
            2. Ensure return types are identical to examples (int vs float, list vs tuple, etc.).
            3. Remove any unnecessary complexity or over-engineering.
            4. Confirm no imports are included (they will be auto-added during verification).
            5. Return ONLY the clean function body, ready for testing.
            This is your last chance to fix type mismatches or signature errors.""",
            context=final_solution
        )

        return polished_solution