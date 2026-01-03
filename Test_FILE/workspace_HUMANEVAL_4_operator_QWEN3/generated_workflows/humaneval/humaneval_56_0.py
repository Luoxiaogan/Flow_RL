# Workflow ID: humaneval_56_0
# Benchmark: humaneval
# Data Indices: [12, 81]

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
        
        # PHASE 1: DECOMPOSE — Extract structured understanding
        decomposition = await self.generate(
            instruction="""You are a senior software engineer reverse-engineering a function from its specification. Analyze the docstring examples and signature to extract:

1. Exact parameter types and names
2. Expected return type (be precise: int, float, str, None, list, etc.)
3. Behavioral pattern: What transformation or selection is being applied?
4. Edge cases: What inputs trigger special behavior? (empty list, zero, None, etc.)
5. Algorithmic hint: Is this a lookup, reducer, mapper, filter, or mathematical formula?
6. Constraints: Any performance, style, or minimalism requirements?

Format your response as a structured analysis with clear sections. Do not generate code yet — only understanding.""",
            context=""
        )

        # PHASE 2: PARALLEL GENERATION — Three strategies in parallel
        literal_strategy = self.generate(
            instruction=f"""Generate Python code using LITERAL TRANSLATION STRATEGY:
- Directly map examples to code structures
- If examples show discrete mappings (e.g., 4.0 → 'A+'), use explicit conditionals or lookup
- Prioritize example fidelity over elegance
- Handle edge cases first as shown in examples
- Return type must match examples exactly (None vs '', int vs float)
- Function name must match ENTRY POINT exactly

Context: {decomposition}""",
            context=decomposition
        )

        algorithmic_strategy = self.generate(
            instruction=f"""Generate Python code using ALGORITHMIC GENERALIZATION STRATEGY:
- Infer the underlying mathematical or logical rule from examples
- Use built-in functions (max, min, filter, etc.) where appropriate
- Optimize for clarity and generality
- Still handle all edge cases from examples
- Return type must match examples exactly
- Function name must match ENTRY POINT exactly

Context: {decomposition}""",
            context=decomposition
        )

        edge_first_strategy = self.generate(
            instruction=f"""Generate Python code using EDGE-CASE FIRST STRATEGY:
- Start by handling all edge cases shown in examples (empty input, zeros, None, etc.)
- Then implement general case
- Use guard clauses and early returns
- Ensure no over-engineering — minimal code that satisfies examples
- Return type must match examples exactly
- Function name must match ENTRY POINT exactly

Context: {decomposition}""",
            context=decomposition
        )

        # Execute all three in parallel
        literal_code, algorithmic_code, edge_code = await asyncio.gather(
            literal_strategy, algorithmic_strategy, edge_first_strategy
        )

        # PHASE 3: ENSEMBLE — Synthesize best solution
        best_solution = await self.ensemble(
            instruction="""You are the lead architect selecting the best implementation. Evaluate these three candidates:

1. Correctness: Does it handle all examples and edge cases?
2. Precision: Does return type match exactly? (e.g., None not '', int not float)
3. Minimalism: No extra logic, imports, or comments
4. Readability: Clear and maintainable
5. Function name: Must match ENTRY POINT exactly

If one is clearly best, select it. If multiple have strengths, synthesize a hybrid. Return ONLY the function body as clean Python code — no explanations, no imports, no markdown.""",
            contexts_list=[literal_code, algorithmic_code, edge_code]
        )

        # PHASE 4: ITERATIVE REFINEMENT — Up to 2 rounds of polishing
        current_code = best_solution
        for i in range(2):
            critique = await self.revise(
                instruction=f"""Critique this code against the original specification:

1. Does it pass all examples in the docstring?
2. Are edge cases handled exactly as shown?
3. Is return type precise? (e.g., returns None not 'None', float not int)
4. Is function name exactly as specified in ENTRY POINT?
5. Any over-engineering? Remove unnecessary logic.
6. Any under-engineering? Add missing edge case handling.

If no issues, respond with 'APPROVED'. Otherwise, return the corrected code body only.""",
                context=current_code
            )
            
            if "APPROVED" in critique.upper():
                break
            current_code = critique

        return current_code