# Workflow ID: humaneval_2_0
# Benchmark: humaneval
# Data Indices: [122, 134]

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

        # Step 1: Deep problem decomposition
        analysis = await self.generate(
            instruction="""Perform a comprehensive analysis of this code generation problem. Structure your response as follows:

1. FUNCTION SIGNATURE: Extract exact function name and parameters
2. INPUT/OUTPUT TYPES: Identify expected types from examples
3. CORE LOGIC: Describe the transformation or computation required
4. EXAMPLE BREAKDOWN: For each example, explain what it demonstrates
5. EDGE CASES: List all edge cases implied by examples or constraints
6. ALGORITHM OPTIONS: Suggest 2-3 different implementation approaches
7. CONSTRAINTS: List all explicit and implicit constraints
8. POTENTIAL PITFALLS: What could go wrong? Type mismatches? Off-by-one? Boundary errors?

Be exhaustive. The quality of subsequent steps depends on this analysis.""",
            context=""
        )

        # Step 2: Parallel solution generation from different perspectives
        solution_attempts = await asyncio.gather(
            self.generate(
                instruction=f"""Generate a Python function implementation based on this analysis:
{analysis}

Approach 1: Direct and literal interpretation. Follow examples exactly. Use simplest possible logic. Prioritize readability over cleverness. Include no extra features or optimizations.

IMPORTANT: 
- Function name must match ENTRY POINT exactly
- Return type must match examples precisely
- Handle all edge cases identified in analysis
- Code must be self-contained (no external dependencies unless imported inside this function)
- Return ONLY the function code, nothing else""",
                context=analysis
            ),
            self.generate(
                instruction=f"""Generate a Python function implementation based on this analysis:
{analysis}

Approach 2: Robust and defensive. Add explicit checks for edge cases. Use more verbose but safer logic. Consider input validation even if not explicitly required. Handle potential type conversions explicitly.

IMPORTANT: 
- Function name must match ENTRY POINT exactly
- Return type must match examples precisely
- Handle all edge cases identified in analysis
- Code must be self-contained
- Return ONLY the function code, nothing else""",
                context=analysis
            ),
            self.generate(
                instruction=f"""Generate a Python function implementation based on this analysis:
{analysis}

Approach 3: Optimized and concise. Use Python idioms, comprehensions, or built-ins where appropriate. Prioritize brevity and elegance while maintaining correctness. Assume inputs meet constraints unless examples show otherwise.

IMPORTANT: 
- Function name must match ENTRY POINT exactly
- Return type must match examples precisely
- Handle all edge cases identified in analysis
- Code must be self-contained
- Return ONLY the function code, nothing else""",
                context=analysis
            )
        )

        # Step 3: Ensemble selection with justification
        selected_solution = await self.ensemble(
            instruction="""Select the best solution from the candidates below. Your selection criteria:

1. CORRECTNESS: Which solution best matches all examples in the specification?
2. EDGE CASE HANDLING: Which solution explicitly handles all identified edge cases?
3. SIMPLICITY: Prefer simpler, more direct solutions unless complexity is justified
4. TYPE SAFETY: Which solution ensures correct return types (int vs float, etc.)?
5. ADHERENCE: Which solution follows the specification exactly without over-engineering?

Provide your selection as just the index (0, 1, or 2) of the best candidate, followed by a brief justification (1-2 sentences).""",
            contexts_list=solution_attempts
        )

        # Extract selected solution (parse index from ensemble response)
        try:
            selected_index = int(re.search(r'[0-2]', selected_solution).group())
            chosen_code = solution_attempts[selected_index]
        except:
            # Fallback: use first solution if parsing fails
            chosen_code = solution_attempts[0]

        # Step 4: Revision with simulated test case validation
        refined_code = await self.revise(
            instruction=f"""Critically review this code solution:

{chosen_code}

Perform a line-by-line validation against the problem specification:

1. Does the function name exactly match the ENTRY POINT?
2. Does it handle ALL examples shown in the docstring correctly?
3. Are edge cases from the analysis properly addressed?
4. Is the return type correct (int vs float, etc.)?
5. Is there any over-engineering or unnecessary complexity?
6. Are there any potential bugs or logical errors?

If any issues are found, provide the corrected code. If no issues, return the original code unchanged.

IMPORTANT: Return ONLY the function code, nothing else.""",
            context=chosen_code
        )

        # Step 5: Final cleanup and standardization
        final_code = await self.summarize(
            instruction="""Extract ONLY the Python function code from the text below. Remove any explanations, markdown, or extra text. Ensure:

1. Function signature exactly matches ENTRY POINT
2. Code is properly indented
3. No extra imports or helper functions unless absolutely necessary
4. Return type matches specification
5. Clean, minimal, and directly executable

Return ONLY the function code, nothing else.""",
            context=refined_code
        )

        return final_code