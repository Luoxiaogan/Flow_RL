# Workflow ID: mbppplus_116_0
# Benchmark: mbppplus
# Data Indices: [15, 270, 46]

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

        # PHASE 1: PARALLEL PERSPECTIVE GENERATION
        # Generate three complementary analyses in parallel
        intent_analysis, structure_analysis, idiom_analysis = await asyncio.gather(
            self.generate(
                instruction="""Analyze the core intent of this programming task:
                - What transformation, validation, or computation is being requested?
                - What would constitute success? What are the failure modes?
                - Extract any explicit or implicit rules from the test cases.
                - Consider edge cases: empty inputs, single elements, boundary values.
                Format as a structured bullet-point analysis.""",
                context=""
            ),
            self.generate(
                instruction="""Analyze the data structures and constraints:
                - What are the input types and expected output types?
                - Are there type conversion requirements?
                - What are the size/length constraints?
                - Are there ordering or uniqueness requirements?
                - How should edge cases (empty, null, extreme values) be handled?
                Format as a structured bullet-point analysis.""",
                context=""
            ),
            self.generate(
                instruction="""Identify potential Python implementation approaches:
                - What built-in functions, operators, or language features could be used?
                - Are there relevant standard library modules (re, itertools, etc.)?
                - What are common Python idioms for this type of problem?
                - Suggest 2-3 alternative implementation strategies.
                Format as a structured bullet-point analysis.""",
                context=""
            )
        )

        # PHASE 2: SYNTHESIZE UNIFIED SPECIFICATION
        synthesized_spec = await self.ensemble(
            instruction="""Synthesize a comprehensive implementation specification:
            Combine insights from the three analyses:
            1. Core intent and success criteria
            2. Data structure constraints and edge case handling
            3. Recommended implementation approaches and Python idioms
            
            Create a unified, detailed specification that:
            - Precisely defines the function's behavior
            - Specifies how to handle all edge cases
            - Recommends the most appropriate implementation strategy
            - Includes specific examples of input/output transformations
            
            Format as a clear, structured specification document.""",
            contexts_list=[intent_analysis, structure_analysis, idiom_analysis]
        )

        # PHASE 3: PARALLEL CODE GENERATION (PURE vs LIBRARY)
        pure_code, library_code = await asyncio.gather(
            self.generate(
                instruction=f"""Generate a PURE PYTHON implementation:
                Based on this specification:
                {synthesized_spec}
                
                Requirements:
                - Use only built-in Python (no imports beyond what's absolutely necessary)
                - Prefer comprehensions, loops, and built-in functions
                - Handle all edge cases explicitly
                - Include clear variable names and minimal comments
                - Return exactly the required data type (list, tuple, etc.)
                
                Output ONLY the function implementation with necessary imports at top.
                No explanations, no markdown, just code.""",
                context=synthesized_spec
            ),
            self.generate(
                instruction=f"""Generate a LIBRARY-ASSISTED implementation:
                Based on this specification:
                {synthesized_spec}
                
                Requirements:
                - Use appropriate Python standard library modules if beneficial (re, itertools, etc.)
                - Leverage library functions for efficiency and clarity
                - Handle all edge cases explicitly
                - Include necessary imports at top
                - Return exactly the required data type (list, tuple, etc.)
                
                Output ONLY the function implementation with necessary imports at top.
                No explanations, no markdown, just code.""",
                context=synthesized_spec
            )
        )

        # PHASE 4: VALIDATION & REVISION LOOP (max 2 iterations)
        candidates = [pure_code, library_code]
        for iteration in range(2):
            # Validate each candidate in parallel
            validations = await asyncio.gather(
                *[self.revise(
                    instruction="""Critically evaluate this implementation:
                    - Does it correctly handle all specified edge cases?
                    - Is the return type exactly as required?
                    - Are there any logical errors or off-by-one mistakes?
                    - Could it fail on any implicit test cases not shown?
                    - Is it efficient and readable?
                    
                    If any issues are found, describe them specifically.
                    If no issues, state "VALID: No issues found".
                    
                    Focus on concrete, actionable feedback.""",
                    context=candidate
                ) for candidate in candidates]
            )
            
            # Check if any validation found issues
            needs_revision = False
            for i, validation in enumerate(validations):
                if "VALID:" not in validation.upper() or "NO ISSUES" not in validation.upper():
                    needs_revision = True
                    # Revise this candidate
                    candidates[i] = await self.revise(
                        instruction=f"""Revise this implementation based on the critique:
                        Critique: {validation}
                        
                        Requirements:
                        - Fix all identified issues
                        - Maintain the original approach (pure/library) unless fundamentally flawed
                        - Preserve handling of all edge cases
                        - Keep code clean and Pythonic
                        
                        Output ONLY the revised function implementation.
                        No explanations, no markdown, just code.""",
                        context=candidates[i]
                    )
            
            if not needs_revision:
                break  # Exit early if both are valid

        # PHASE 5: FINAL ENSEMBLE SELECTION
        final_code = await self.ensemble(
            instruction="""Select the best implementation:
            Compare these two candidates:
            - Which one is more robust and handles edge cases better?
            - Which one is more readable and Pythonic?
            - Which one is more efficient for typical use cases?
            - If both are valid, prefer the simpler, more straightforward approach.
            
            Output ONLY the selected function implementation.
            No explanations, no markdown, just code.""",
            contexts_list=candidates
        )

        return final_code