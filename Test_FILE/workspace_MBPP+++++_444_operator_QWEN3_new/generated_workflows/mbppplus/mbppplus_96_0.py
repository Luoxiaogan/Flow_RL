# Workflow ID: mbppplus_96_0
# Benchmark: mbppplus
# Data Indices: [366, 361, 22]

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

        # Step 1: Deep problem decomposition into structured schema
        decomposition = await self.generate(
            instruction="""Perform a comprehensive structural analysis of this programming problem. Extract and format the following in a clear, line-delimited schema (not JSON):

1. INPUT_TYPE: What data types are inputs? (e.g., string, int, list of ints)
2. OUTPUT_TYPE: What is the expected return type? (e.g., string, int, list)
3. CORE_OPERATION: What fundamental operation is required? (e.g., filtering, mapping, mathematical formula, set operation)
4. CONSTRAINTS: Any explicit or implicit constraints (e.g., "must handle negative numbers", "case-insensitive")
5. EDGE_CASES: List at least 3 critical edge cases (e.g., empty input, single element, boundary values)
6. FUNCTION_SIGNATURE: Extract the exact function name and parameters from the problem
7. PERFORMANCE_HINT: Any efficiency requirements or hints (e.g., "avoid O(n^2)", "use math formula")

Format each line as "KEY: value" and be precise. This schema will drive all subsequent reasoning.""",
            context=""
        )

        # Step 2: Generate three parallel solution strategies with different cognitive roles
        strategy_tasks = [
            self.generate(
                instruction=f"""You are a MATHEMATICIAN. Given this problem schema:
{decomposition}

Derive an elegant, formula-based solution. Focus on:
- Mathematical insights or closed-form expressions
- Algebraic simplifications
- Avoid brute force when possible
- Handle edge cases mathematically
Output only the core logic in pseudocode with brief annotations.""",
                context=""
            ),
            self.generate(
                instruction=f"""You are a SYSTEMATIC PROGRAMMER. Given this problem schema:
{decomposition}

Write a robust, step-by-step solution. Focus on:
- Clear, readable code structure
- Explicit handling of all edge cases listed
- Defensive programming (input validation, type checks)
- Iterative or conditional logic as needed
Output only the core logic in pseudocode with brief annotations.""",
                context=""
            ),
            self.generate(
                instruction=f"""You are a TEST-DRIVEN DEVELOPER. Given this problem schema:
{decomposition}

Design a solution by first writing test cases, then implementing to pass them. Focus on:
- Generate 3-5 critical test cases (including edge cases)
- Write minimal code to pass each test incrementally
- Refactor for clarity after all tests pass
Output test cases first, then implementation in pseudocode.""",
                context=""
            )
        ]
        
        strategy_results = await asyncio.gather(*strategy_tasks)

        # Step 3: Critique and refine each strategy
        refined_strategies = []
        for i, strategy in enumerate(strategy_results):
            refined = await self.revise(
                instruction=f"""Critically evaluate and improve this solution strategy:

{strategy}

Apply these revision criteria:
1. Does it correctly handle ALL edge cases from the schema?
2. Is the return type exactly as specified?
3. Are there any off-by-one errors or boundary issues?
4. Could it be made more efficient without losing correctness?
5. Is the logic clear and free of ambiguity?
6. Does it match the function signature exactly?

Output only the revised, improved version. Be brutally honest in your critique.""",
                context=strategy
            )
            refined_strategies.append(refined)

        # Step 4: Ensemble synthesis - merge the best elements
        synthesized = await self.ensemble(
            instruction=f"""Synthesize a final solution by combining the strongest elements from these three approaches:

Approach 1 (Mathematician): {refined_strategies[0]}

Approach 2 (Systematic Programmer): {refined_strategies[1]}

Approach 3 (Test-Driven Developer): {refined_strategies[2]}

Your synthesis must:
1. Preserve mathematical elegance where possible
2. Incorporate robust edge case handling
3. Maintain clean, readable structure
4. Include any critical test cases as comments
5. Output ONLY the final Python function implementation with exact signature
6. Include necessary imports at top if any (e.g., import math)
7. NO extra text, explanations, or markdown - just code

The function must be production-ready and pass all test cases.""",
            contexts_list=refined_strategies
        )

        # Step 5: Validate and clean output format
        final_code = await self.revise(
            instruction="""Ensure this code meets EXACT output requirements:
1. Contains ONLY the function implementation (no extra text)
2. Uses EXACT function name and parameters from problem
3. Includes imports at top if needed (inside function is ok)
4. Returns correct data type (list vs tuple vs set matters)
5. Handles all edge cases (empty inputs, single elements, etc.)
6. No print statements or debug code
7. Clean, PEP8-compliant formatting

If any requirement is violated, fix it immediately. Output only the corrected code.""",
            context=synthesized
        )

        # Step 6: Final safety check - ensure function name matches
        function_line_check = await self.generate(
            instruction=f"""Verify that this code contains the EXACT function signature from the problem.
If not, regenerate with correct signature.

Code to check:
{final_code}

Output ONLY the corrected code with proper function signature. No explanations.""",
            context=final_code
        )

        return function_line_check