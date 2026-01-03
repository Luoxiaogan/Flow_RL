# Workflow ID: humaneval_32_0
# Benchmark: humaneval
# Data Indices: [161, 80]

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

        # PHASE 1: DECOMPOSE SPECIFICATION
        decomposition = await self.generate(
            instruction="""Thoroughly decompose the problem specification into structured components. Extract:
            1. Function signature and exact ENTRY POINT name (MUST match)
            2. Core behavior: What should the function do under normal conditions?
            3. Edge cases: What special conditions must be handled? (e.g., empty input, no letters, length < 3)
            4. Return type: Must match examples exactly (int, float, str, bool)
            5. Algorithmic primitives: What operations are implied? (e.g., case reversal, sliding window, distinctness check)
            6. Examples breakdown: Translate each example into a test case description.
            Format as a bulleted list with clear section headers. Be exhaustive.""",
            context=""
        )

        # PHASE 2: PARALLEL GENERATION (3 DIVERSE ATTEMPTS)
        generation_instructions = [
            """Generate a solution that strictly follows the examples literally. 
            Implement exactly what is demonstrated in the examples, no generalization. 
            Prioritize example fidelity over elegance. Handle edge cases explicitly as shown.""",
            
            """Generate a solution that generalizes the pattern from examples. 
            Infer the underlying rule and implement it robustly. 
            Use clear variable names and comments explaining the logic. 
            Assume hidden test cases will stress edge conditions.""",
            
            """Generate a defensive solution that explicitly checks all edge cases mentioned in the spec. 
            Use guard clauses, explicit conditionals, and verbose validation. 
            Prioritize correctness over performance or brevity. 
            Include comments for each edge case handled."""
        ]

        solution_attempts = await asyncio.gather(
            *[self.generate(instruction=inst, context=decomposition) for inst in generation_instructions]
        )

        # PHASE 3: PARALLEL VALIDATION
        validation_instruction = f"""Critically review this code against the decomposed specification:
        - Does it use the exact ENTRY POINT function name?
        - Does it handle ALL edge cases extracted in decomposition?
        - Does return type match examples exactly?
        - Are there any logical gaps or off-by-one errors?
        - Is it over-engineered? (Must implement ONLY what's specified)
        If flaws exist, revise the code to fix them. Return the corrected version.
        If no flaws, return the code unchanged."""

        validated_solutions = await asyncio.gather(
            *[self.revise(instruction=validation_instruction, context=sol) for sol in solution_attempts]
        )

        # PHASE 4: ENSEMBLE SELECTION
        final_selection = await self.ensemble(
            instruction="""Select the single best solution from the candidates. Criteria:
            1. Correctness: Must handle all edge cases and match return types.
            2. Fidelity: Must use exact ENTRY POINT name and follow spec precisely.
            3. Robustness: Least likely to fail on hidden test cases.
            4. Simplicity: No over-engineering, minimal and clean.
            Return ONLY the selected code block, nothing else.""",
            contexts_list=validated_solutions
        )

        # PHASE 5: FINAL POLISH
        polished_code = await self.revise(
            instruction="""Minify and clean this code for production:
            - Remove all comments and debug prints
            - Use minimal variable names (single letters if clear)
            - Ensure no extra whitespace or blank lines
            - Verify function name matches ENTRY POINT exactly
            - Return type must be consistent with examples
            Output ONLY the raw Python code, nothing else.""",
            context=final_selection
        )

        return polished_code