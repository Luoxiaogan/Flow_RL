# Workflow ID: humaneval_46_0
# Benchmark: humaneval
# Data Indices: [65, 6]

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
        Universal workflow for generating Python functions from docstring specifications.
        Uses dynamic instruction generation, parallel strategy exploration, and iterative refinement.
        """
        import asyncio
        import re

        # PHASE 1: Extract and expand the specification
        spec_analysis = await self.generate(
            instruction="""Thoroughly analyze the function specification and docstring examples.
            1. List all explicit requirements mentioned in the docstring.
            2. Infer implicit constraints and edge cases from the examples.
            3. Identify the exact expected return type (string, int, list, etc.) from examples.
            4. Note any special conditions (e.g., "if shift > digits, reverse").
            5. Generate 3-5 plausible edge cases not shown in examples (consider: empty input, zero, max values, type boundaries).
            6. Extract the exact function name that must be used.
            Format as a structured markdown list with clear sections.""",
            context=""
        )

        # PHASE 2: Generate multiple implementation strategies in parallel
        strategy_instructions = [
            """Generate a Python function implementation that:
            - Follows the literal pattern shown in the examples
            - Uses simple, direct logic
            - Handles only the explicitly shown cases first
            - Is minimal and avoids over-engineering
            - Uses the exact function name specified
            - Returns the exact type shown in examples (string, int, etc.)""",
            
            """Generate a Python function implementation that:
            - Generalizes the pattern mathematically or algorithmically
            - Handles edge cases proactively (including those inferred in spec analysis)
            - Uses optimal Python features (slicing, comprehensions, built-ins)
            - Is robust to boundary conditions
            - Uses the exact function name specified
            - Returns the exact type shown in examples""",
            
            """Generate a Python function implementation that:
            - Focuses on edge case handling first
            - Uses defensive programming for inferred edge cases
            - Is explicit and verbose in logic (for clarity)
            - Uses the exact function name specified
            - Returns the exact type shown in examples
            - Includes inline comments explaining key decisions"""
        ]

        strategy_candidates = await asyncio.gather(
            *[self.generate(instruction=instr, context=spec_analysis) for instr in strategy_instructions]
        )

        # PHASE 3: Critique and refine each candidate
        refined_candidates = []
        for i, candidate in enumerate(strategy_candidates):
            critique = await self.revise(
                instruction=f"""Critically evaluate this implementation candidate:
                1. Does it handle ALL inferred edge cases from the spec analysis?
                2. Is the return type EXACTLY as shown in examples (string vs int matters)?
                3. Does it use the correct function name?
                4. Is it minimal (no extra features)?
                5. Are there any logical flaws or boundary condition misses?
                6. Is the code clean and Pythonic?
                Fix any issues found. Return only the corrected code.""",
                context=candidate
            )
            refined_candidates.append(critique)

        # PHASE 4: Ensemble synthesis - select and merge best parts
        final_implementation = await self.ensemble(
            instruction="""Select the best implementation from the candidates, or synthesize a new one by combining their strongest parts.
            Selection criteria:
            - Must pass all example cases shown in docstring
            - Must handle inferred edge cases
            - Must use exact function name
            - Must return exact type shown in examples
            - Prioritize correctness over elegance
            - Avoid over-engineering
            Return ONLY the final Python function code, nothing else.""",
            contexts_list=refined_candidates
        )

        # PHASE 5: Final validation simulation and polish
        validated_implementation = await self.revise(
            instruction=f"""Final polish and validation:
            1. Verify function name matches exactly what's required.
            2. Verify return type matches examples exactly (string, int, list, etc.).
            3. Simulate running the examples from the docstring - does output match?
            4. Check for any remaining edge cases from spec analysis.
            5. Remove any unnecessary comments or debug code.
            6. Ensure code is minimal and matches specification exactly.
            Return only the final, polished code.""",
            context=final_implementation
        )

        return validated_implementation