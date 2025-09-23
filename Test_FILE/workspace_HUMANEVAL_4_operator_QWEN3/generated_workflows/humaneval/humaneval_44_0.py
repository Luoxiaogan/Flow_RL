# Workflow ID: humaneval_44_0
# Benchmark: humaneval
# Data Indices: [75, 53]

# --- DO NOT IMPORT HERE ---
class Workflow:
    def __init__(self, config, problem) -> None:
        # --- DO NOT MODIFY THIS SECTION ---
        self.config = config
        self.problem_text = problem
        self.llm = create(config)
        
        self.generate = operator.Generate(self.llm, self.problem_text)
        self.revise = operator.Revise(self.llm, self.problem_text)
        self.summarize = operator.Summarize(self.llm, self.problem_text)
        self.ensemble = operator.Ensemble(self.llm, self.problem_text)

    async def run_workflow(self):
        """
        Universal code generation workflow that adapts strategy based on problem complexity.
        Handles everything from trivial arithmetic to complex algorithmic problems.
        """
        import asyncio
        import re

        # PHASE 1: STRUCTURED PROBLEM ANALYSIS
        analysis = await self.generate(
            instruction="""Perform deep structural analysis of the problem specification. Extract and organize:

1. FUNCTION SIGNATURE: Exact name, parameters, and return type hints if any.
2. EXAMPLES: Parse all >>> examples into input-output pairs. Identify patterns or transformations.
3. CONSTRAINTS: Explicit limits (e.g., 'a < 100'), implicit bounds, edge cases mentioned or implied.
4. SEMANTIC COMPLEXITY: Is the output directly computable from inputs (trivial) or does it require internal logic/loops/helpers (algorithmic)? Justify.
5. RETURN TYPE: Must match examples exactly (int vs float matters). Infer from examples if not specified.
6. EDGE CASES: What boundary values must be handled? (0, 1, negatives, empties, etc.)

Format as a structured JSON-like outline with clear section headers.""",
            context=""
        )

        # PHASE 2: STRATEGY CLASSIFICATION (Conditional Branching)
        strategy = await self.generate(
            instruction=f"""Based on this analysis:
{analysis}

Classify this problem into one of two STRATEGIES:
- "TRIVIAL": Output is directly computable from inputs via basic operations (arithmetic, string concat, etc.) with no hidden state or iteration. Examples show direct mapping.
- "ALGORITHMIC": Requires internal logic, loops, helper functions, or stateful computation. Examples imply decomposition or multi-step reasoning.

Respond ONLY with "TRIVIAL" or "ALGORITHMIC".""",
            context=analysis
        )

        # PHASE 3A: TRIVIAL PATH (Direct Implementation)
        if "TRIVIAL" in strategy.upper():
            initial_solution = await self.generate(
                instruction=f"""Generate the minimal, correct Python function based EXACTLY on the specification.

Guidelines:
- Use the exact function name from ENTRY POINT.
- Match return types precisely (int/float/bool/string) as shown in examples.
- Handle edge cases identified in analysis (e.g., 0, empty inputs).
- No over-engineering: implement ONLY what's specified.
- Include no extra comments or explanations — just the function.

Example of expected format:
def add(x: int, y: int):
    return x + y""",
                context=analysis
            )

            # Single revision for type safety and edge cases
            final_solution = await self.revise(
                instruction="""Critique this code for:
1. TYPE SAFETY: Do return types exactly match examples? (e.g., int vs float)
2. EDGE CASES: Does it handle 0, 1, negatives, or other boundaries mentioned?
3. EXAMPLE COMPLIANCE: Does it reproduce ALL example outputs exactly?
4. SYNTAX: Is it valid Python with correct indentation?

If any issue is found, revise the code to fix it. Otherwise, return unchanged.""",
                context=initial_solution
            )

        # PHASE 3B: ALGORITHMIC PATH (Parallel Generation + Ensemble)
        else:
            # Generate 3 candidate solutions in parallel
            candidate_tasks = [
                self.generate(
                    instruction=f"""Generate a correct Python implementation using BRUTE FORCE approach.

Guidelines:
- Use the exact function name from ENTRY POINT.
- Helper functions are allowed if needed (define inside main function or globally as appropriate).
- Prioritize correctness over efficiency (within reason).
- Handle all edge cases from analysis.
- Include no extra comments — just working code.

Example structure for prime problem:
def is_multiply_prime(a):
    def is_prime(n):
        if n < 2: return False
        for i in range(2, int(n**0.5)+1):
            if n % i == 0: return False
        return True
    # ... rest of logic""",
                    context=analysis
                ),
                self.generate(
                    instruction=f"""Generate a correct Python implementation using MATHEMATICAL OPTIMIZATION.

Guidelines:
- Use mathematical insights to reduce computation (e.g., precompute primes, use symmetry).
- Still ensure correctness for all cases under constraints (e.g., a < 100).
- Define helper functions if needed.
- Match return types exactly.
- No comments — just code.""",
                    context=analysis
                ),
                self.generate(
                    instruction=f"""Generate a correct Python implementation using EXAMPLE-DRIVEN REASONING.

Guidelines:
- Analyze the provided examples to infer patterns or invariants.
- Build solution by generalizing from examples.
- Handle edge cases explicitly.
- Use clear, readable logic even if less efficient.
- Exact function signature and return types required.""",
                    context=analysis
                )
            ]

            candidates = await asyncio.gather(*candidate_tasks)

            # Ensemble: Select best or synthesize hybrid
            final_solution = await self.ensemble(
                instruction=f"""Evaluate these 3 candidate solutions:

1. Analyze each for:
   - Correctness on ALL examples from specification
   - Edge case handling (0, 1, boundaries)
   - Return type precision
   - Code clarity and maintainability

2. If one candidate is clearly superior, select it.
3. If multiple are good, SYNTHESIZE a hybrid that combines their strengths.
4. Ensure final code has exact function name and no syntax errors.

Return ONLY the final code — no explanations.""",
                contexts_list=candidates
            )

            # One revision pass for final polish
            final_solution = await self.revise(
                instruction="""Final quality check:
1. Verify function name matches ENTRY POINT exactly.
2. Confirm all examples from specification are handled correctly.
3. Check for off-by-one errors, loop bounds, and edge cases.
4. Ensure no unused imports or variables.
5. Fix any syntax or indentation issues.

Return the polished code.""",
                context=final_solution
            )

        return final_solution