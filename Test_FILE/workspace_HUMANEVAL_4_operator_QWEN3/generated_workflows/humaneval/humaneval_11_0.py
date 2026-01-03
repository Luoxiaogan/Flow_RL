# Workflow ID: humaneval_11_0
# Benchmark: humaneval
# Data Indices: [59, 141]

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

        # STEP 1: Comprehensive Problem Analysis
        analysis = await self.generate(
            instruction="""Perform deep structural analysis of this code generation problem. Extract and organize:

1. FUNCTION SIGNATURE: Exact name, parameters, return type
2. REQUIREMENTS: Explicit rules from docstring
3. EXAMPLES: Input-output pairs and what they reveal
4. EDGE CASES: Implied boundaries (empty, zero, max, min, invalid)
5. ALGORITHM TYPE: Mathematical, string, list, logical, hybrid
6. HELPER NEEDS: Does it require auxiliary functions? (e.g., is_prime)
7. TYPE CONSTRAINTS: Must return int? float? string? exact match?
8. COMMON PITFALLS: What usually goes wrong in similar problems?

Format as structured markdown with clear section headers.""",
            context=""
        )

        # STEP 2: Parallel Solution Generation - Two Divergent Strategies
        solution_attempts = await asyncio.gather(
            self.generate(
                instruction=f"""Generate Python code implementing the function based on analysis:
{analysis}

STRATEGY 1: LITERAL INTERPRETATION
- Follow examples exactly
- Prioritize correctness over elegance
- Include all edge case handling explicitly
- Use verbose variable names for clarity
- Return code ONLY (no explanations) in a Python code block""",
                context=analysis
            ),
            self.generate(
                instruction=f"""Generate Python code implementing the function based on analysis:
{analysis}

STRATEGY 2: PATTERN GENERALIZATION
- Infer underlying algorithm from examples
- Optimize for efficiency and elegance
- Use mathematical/formulaic approaches where possible
- Abstract common operations into helper functions if needed
- Return code ONLY (no explanations) in a Python code block""",
                context=analysis
            )
        )

        # STEP 3: Ensemble Synthesis
        synthesized = await self.ensemble(
            instruction="""Merge the two solution attempts into one optimal implementation:

CRITERIA:
1. CORRECTNESS: Must handle all examples and edge cases from analysis
2. EFFICIENCY: Prefer O(n) over O(n²), avoid unnecessary computation
3. READABILITY: Clear variable names, logical structure
4. ROBUSTNESS: Explicit type handling, boundary checks
5. MINIMALISM: No over-engineering - implement exactly what's specified

CONFLICT RESOLUTION:
- If one handles edge cases better, adopt that logic
- If one is more efficient, adopt that structure
- Combine strengths, eliminate redundancies
- Ensure function name matches ENTRY POINT exactly

Output ONLY the final Python code in a code block.""",
            contexts_list=solution_attempts
        )

        # STEP 4: Iterative Self-Critique (Max 2 revisions)
        current_code = synthesized
        for iteration in range(2):
            critique = await self.generate(
                instruction=f"""Critically review this code against the original specification:

ANALYSIS CONTEXT:
{analysis}

CODE TO REVIEW:
{current_code}

CHECKLIST:
1. Does function name match ENTRY POINT exactly?
2. Do all docstring examples work? (Trace execution manually)
3. Are return types correct? (int vs float, string exact match)
4. Are edge cases from analysis handled?
5. Any off-by-one errors? Infinite loops? Division by zero?
6. Is there any over-engineering? (Extra features not specified)
7. Are helper functions properly defined if needed?

If ANY issues found, describe them specifically. If perfect, say 'VALID'.""",
                context=current_code
            )
            
            if "VALID" in critique.upper() and "ISSUE" not in critique.upper():
                break
                
            current_code = await self.revise(
                instruction=f"""Revise the code to fix these specific issues:
{critique}

Preserve correct parts. Only change what's necessary.
Output ONLY the corrected Python code in a code block.""",
                context=current_code
            )

        # STEP 5: Final Validation Script Generation (Meta-Check)
        final_output = await self.revise(
            instruction="""Final polish:

1. Ensure code is wrapped in