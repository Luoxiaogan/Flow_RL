# Workflow ID: humaneval_81_0
# Benchmark: humaneval
# Data Indices: [143, 32]

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

        # Phase 1: Problem Deconstruction and Typing
        deconstruction = await self.generate(
            instruction="""Thoroughly analyze the problem specification. Extract and structure the following:
            1. Function signature and exact entry point name (MUST match)
            2. All example input-output pairs - list them explicitly
            3. Constraints and edge case hints (e.g., length limits, type requirements)
            4. Domain keywords (e.g., 'prime', 'polynomial', 'sentence', 'zero point')
            5. Inferred problem category (string manipulation, mathematical, algorithmic, etc.)
            6. Suggested solution approaches based on examples and constraints
            Format as a structured analysis with clear section headers.""",
            context=""
        )

        # Phase 2: Parallel Strategy Generation (Diamond Pattern)
        strategy_instructions = [
            """Generate a LITERAL solution strategy:
            - Directly translate examples into code
            - Replicate exact behavior shown (including type, order, formatting)
            - Do not generalize beyond examples
            - Focus on surface-level pattern matching""",
            
            """Generate an ABSTRACT solution strategy:
            - Derive underlying mathematical/logical pattern
            - Generalize beyond examples to handle all cases
            - Use algorithmic thinking (base cases, recursion, iteration)
            - Prioritize correctness over simplicity""",
            
            """Generate a DEFENSIVE solution strategy:
            - Focus exclusively on edge cases and constraints
            - Handle empty inputs, minimal cases, boundary conditions
            - Add explicit type checks and length validations
            - Assume hidden test cases will target weaknesses"""
        ]

        strategy_candidates = await asyncio.gather(
            *[self.generate(instruction=instr, context=deconstruction) for instr in strategy_instructions]
        )

        # Phase 3: Parallel Implementation & Revision
        implementation_instructions = [
            f"""Implement the function EXACTLY as specified. Critical rules:
            - Function name MUST match ENTRY POINT precisely
            - Return type must match examples (int vs float matters)
            - Handle all constraints mentioned in problem
            - Code must pass hidden test cases
            Strategy context: {strategy}""",
            f"""Implement the function with focus on GENERALIZATION. Critical rules:
            - Must work for cases beyond examples
            - Use clear, maintainable logic
            - Include comments explaining key decisions
            - Validate against constraints
            Strategy context: {strategy}""",
            f"""Implement the function with focus on ROBUSTNESS. Critical rules:
            - Explicitly handle all edge cases
            - Add defensive checks for input validity
            - Ensure no crashes on boundary conditions
            - Prioritize correctness over performance
            Strategy context: {strategy}"""
        ]

        implementations = await asyncio.gather(
            *[self.generate(instruction=instr, context=strat) for instr, strat in zip(implementation_instructions, strategy_candidates)]
        )

        # Phase 4: Parallel Revision (Fix common pitfalls)
        revision_instructions = [
            """Revise this implementation with extreme attention to:
            - EXACT function name matching ENTRY POINT
            - Return type precision (int vs float as in examples)
            - Handling of ALL edge cases mentioned in constraints
            - Correct import statements (add if missing)
            - No over-engineering - implement only what's specified
            Fix any deviations from specification.""",
            """Revise for mathematical/logical correctness:
            - Verify algorithm matches examples
            - Check boundary conditions
            - Ensure numerical precision where required
            - Confirm no off-by-one errors
            - Validate against implicit constraints""",
            """Revise for robustness and edge case handling:
            - Test with minimal inputs (empty, single element)
            - Verify constraint compliance
            - Check type conversions
            - Ensure no unhandled exceptions
            - Confirm output format matches examples exactly"""
        ]

        revised_implementations = await asyncio.gather(
            *[self.revise(instruction=instr, context=impl) for instr, impl in zip(revision_instructions, implementations)]
        )

        # Phase 5: Ensemble Selection
        final_solution = await self.ensemble(
            instruction="""Select the BEST solution from the candidates below. Evaluation criteria:
            1. Correctness: Must satisfy all examples and constraints
            2. Precision: Return types and formats must match exactly
            3. Robustness: Handles edge cases mentioned in problem
            4. Simplicity: No unnecessary complexity or over-engineering
            5. Function name: MUST match ENTRY POINT exactly
            Choose the solution most likely to pass hidden test cases. If multiple are valid, prefer the one with clearest edge case handling.
            Return ONLY the selected code - no explanations.""",
            contexts_list=revised_implementations
        )

        # Phase 6: Validation Feedback Loop (Up to 2 iterations)
        for iteration in range(2):
            validation = await self.generate(
                instruction=f"""Critically evaluate this solution:
                - What edge cases might break it?
                - Are there any type mismatches?
                - Does it handle all constraints?
                - Is the function name exactly correct?
                - What hidden test cases might fail?
                If no issues found, return 'VALID'. Otherwise, list specific flaws.""",
                context=final_solution
            )
            
            if "VALID" in validation.upper() and "FLAW" not in validation.upper() and "ISSUE" not in validation.upper():
                break
                
            final_solution = await self.revise(
                instruction=f"""Fix the following issues identified in validation:
                {validation}
                Preserve correct functionality while addressing flaws.
                Maintain exact function name and return type precision.
                Return ONLY the corrected code.""",
                context=final_solution
            )

        return final_solution