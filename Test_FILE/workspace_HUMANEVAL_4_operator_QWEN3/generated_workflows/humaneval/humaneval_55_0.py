# Workflow ID: humaneval_55_0
# Benchmark: humaneval
# Data Indices: [112, 87]

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

        # Phase 1: Semantic Decomposition
        decomposition = await self.generate(
            instruction="""Thoroughly analyze the problem specification and extract:
1. The exact function signature (name and parameters)
2. Expected return type and structure (e.g., tuple, list, scalar)
3. Core transformation or algorithm described in plain English
4. All edge cases implied by examples (empty inputs, single elements, extremes)
5. Any hidden constraints (performance, immutability, etc.)
6. Potential ambiguities in the specification that need resolution

Format your response as a structured analysis with clear section headers.""",
            context=""
        )

        # Phase 2: Parallel Hypothesis Generation
        literal_approach, pattern_approach, edgecase_approach = await asyncio.gather(
            self.generate(
                instruction=f"""Generate a Python function implementation that:
- Directly mimics the transformations shown in the examples
- Uses explicit, step-by-step logic that mirrors the example inputs/outputs
- Prioritizes clarity and direct correspondence over elegance
- Handles only the cases explicitly shown, but in a way that can be extended

Base your implementation on this analysis:
{decomposition}

Return ONLY the Python function code, no explanations.""",
                context=decomposition
            ),
            self.generate(
                instruction=f"""Generate a Python function implementation that:
- Infers the underlying pattern, formula, or algorithm from the examples
- Uses efficient, generalizable constructs (list comprehensions, built-ins, etc.)
- Abstracts away from specific examples to handle any valid input
- Is concise and mathematically/logically sound

Base your implementation on this analysis:
{decomposition}

Return ONLY the Python function code, no explanations.""",
                context=decomposition
            ),
            self.generate(
                instruction=f"""Generate a Python function implementation that:
- Starts by handling all edge cases first (empty inputs, null values, extremes)
- Then implements the general case, ensuring edge cases remain handled
- Uses defensive programming and explicit conditionals for boundary conditions
- Prioritizes correctness on edge cases over elegance in the general case

Base your implementation on this analysis:
{decomposition}

Return ONLY the Python function code, no explanations.""",
                context=decomposition
            )
        )

        # Phase 3: Parallel Critique and Refinement
        refined_solutions = await asyncio.gather(
            self.revise(
                instruction=f"""Critique and improve this code solution:
1. Verify it matches the exact function signature from the problem
2. Check return type and structure against examples
3. Simulate each example mentally — does it produce the exact expected output?
4. Identify any missing edge cases or logical flaws
5. Improve clarity, efficiency, and Pythonic style without changing behavior
6. Ensure NO over-engineering — implement exactly what's specified

Problem context:
{decomposition}

Revise the code accordingly and return ONLY the improved Python function.""",
                context=literal_approach
            ),
            self.revise(
                instruction=f"""Critique and improve this code solution:
1. Verify it matches the exact function signature from the problem
2. Check return type and structure against examples
3. Simulate each example mentally — does it produce the exact expected output?
4. Identify any missing edge cases or logical flaws
5. Improve clarity, efficiency, and Pythonic style without changing behavior
6. Ensure NO over-engineering — implement exactly what's specified

Problem context:
{decomposition}

Revise the code accordingly and return ONLY the improved Python function.""",
                context=pattern_approach
            ),
            self.revise(
                instruction=f"""Critique and improve this code solution:
1. Verify it matches the exact function signature from the problem
2. Check return type and structure against examples
3. Simulate each example mentally — does it produce the exact expected output?
4. Identify any missing edge cases or logical flaws
5. Improve clarity, efficiency, and Pythonic style without changing behavior
6. Ensure NO over-engineering — implement exactly what's specified

Problem context:
{decomposition}

Revise the code accordingly and return ONLY the improved Python function.""",
                context=edgecase_approach
            )
        )

        # Phase 4: Ensemble Synthesis with Minimalism Constraint
        final_code = await self.ensemble(
            instruction=f"""Synthesize the best possible solution from these three candidates:
{refined_solutions[0]}
---
{refined_solutions[1]}
---
{refined_solutions[2]}

Criteria:
1. Must be minimal — no unnecessary variables, steps, or complexity
2. Must exactly match the function signature and return type specified
3. Must handle all edge cases revealed in examples
4. Prefer list comprehensions, slicing, and built-ins over manual loops
5. Return type must match examples precisely (int vs float, tuple structure, etc.)
6. Code style should be clean, Pythonic, and match reference answer patterns

Return ONLY the final Python function code, no explanations or markdown.""",
            contexts_list=refined_solutions
        )

        # Phase 5: Final Sanitization
        sanitized_code = await self.summarize(
            instruction="""Extract ONLY the Python function code from the following text.
Remove any markdown, explanations, comments, or extra text.
The output must be a clean, runnable Python function that can be directly executed.

Ensure:
- Function name matches ENTRY POINT exactly
- No import statements (they will be added externally)
- No extra whitespace or formatting
- Code is ready for immediate use in testing""",
            context=final_code
        )

        return sanitized_code