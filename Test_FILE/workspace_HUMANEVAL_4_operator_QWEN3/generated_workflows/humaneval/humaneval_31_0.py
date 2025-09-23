# Workflow ID: humaneval_31_0
# Benchmark: humaneval
# Data Indices: [4, 86]

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
        Universal workflow for precise code generation from specifications.
        Handles mathematical, string, list, and algorithmic problems with
        self-correcting, multi-strategy synthesis.
        """
        import asyncio
        import re

        # STEP 1: DECOMPOSE PROBLEM STRUCTURE
        decomposition = await self.generate(
            instruction="""Thoroughly analyze the problem specification. Extract and structure:
            1. Exact function name (MUST match ENTRY POINT)
            2. Input/output types and constraints
            3. Core task in one sentence
            4. Patterns from examples (show input→output transformations)
            5. Edge cases implied (empty inputs, single elements, extreme values)
            6. Forbidden assumptions or common pitfalls
            Format as clear bullet points with headers.""",
            context=""
        )

        # STEP 2: PARALLEL STRATEGY GENERATION
        # Generate 3 distinct solution approaches simultaneously
        strategy_instructions = [
            """Generate a solution using imperative, step-by-step logic.
            Focus on clarity and explicit variable naming.
            Include comments explaining each major step.
            Handle edge cases explicitly with conditionals.""",
            
            """Generate a solution using functional programming style.
            Use comprehensions, map/filter/reduce where appropriate.
            Prioritize conciseness and mathematical elegance.
            Ensure type correctness and precision.""",
            
            """Generate a solution using built-in Python libraries or clever one-liners.
            Leverage sorting, itertools, or other standard library features.
            Optimize for brevity while maintaining readability.
            Include necessary imports inside the function if needed."""
        ]

        strategy_attempts = await asyncio.gather(
            *[self.generate(instruction=instr, context=decomposition) 
              for instr in strategy_instructions]
        )

        # STEP 3: SYNTHESIZE BEST SOLUTION
        synthesized = await self.ensemble(
            instruction=f"""Synthesize a final solution by combining the best elements from all attempts:
            - Take the most reliable core logic
            - Incorporate the most comprehensive edge case handling
            - Adopt the clearest structure and naming
            - Ensure exact function signature matches ENTRY POINT
            - Verify return type matches examples (int vs float matters)
            - Preserve any critical whitespace or ordering requirements
            - Include necessary imports INSIDE the function if used
            Return ONLY the final code block with no additional text.""",
            contexts_list=strategy_attempts
        )

        # STEP 4: REVISE FOR DOMAIN-SPECIFIC CONSTRAINTS
        revised = await self.revise(
            instruction="""Critically revise this code against domain requirements:
            1. Function name MUST exactly match ENTRY POINT (case-sensitive)
            2. Return type must precisely match examples (int/float/str/etc)
            3. Handle all edge cases from decomposition (empty inputs, etc)
            4. No external dependencies unless imported inside function
            5. Code must be self-contained and pass hidden test cases
            6. Preserve exact formatting requirements (whitespace, ordering)
            Fix any violations. Return ONLY the corrected code block.""",
            context=synthesized
        )

        # STEP 5: SELF-TEST VALIDATION (1 iteration)
        validation = await self.generate(
            instruction=f"""Generate 3-5 test assertions that would validate this code.
            Base tests on examples from specification and extrapolate edge cases.
            Format as Python assert statements.
            Then, mentally execute code against these tests - flag any failures.
            If any test would fail, explain why and what needs fixing.
            If all pass, return 'VALIDATED'.""",
            context=f"Problem Decomposition:\n{decomposition}\n\nCode:\n{revised}"
        )

        # Conditional refinement if validation reveals issues
        if "VALIDATED" not in validation:
            final = await self.revise(
                instruction=f"""Fix the code based on validation feedback:
                Validation Issues: {validation}
                Preserve correct parts, only modify what's broken.
                Ensure function name, return type, and edge cases are perfect.
                Return ONLY the final corrected code block.""",
                context=revised
            )
        else:
            final = revised

        return final