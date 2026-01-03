# Workflow ID: humaneval_35_0
# Benchmark: humaneval
# Data Indices: [150, 58]

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
        Adapts strategy based on problem type, validates against examples, and refines output.
        """
        import asyncio
        import re

        # PHASE 1: PROBLEM TYPING & STRATEGY SELECTION (Diamond Pattern)
        # Generate multiple interpretations in parallel
        interpretation_tasks = [
            self.generate(
                instruction="""Analyze the problem as a MATHEMATICAL/LOGICAL function.
                - Identify if decision is based on number properties (prime, even, etc.)
                - Extract decision rules from examples
                - Note edge cases (like n=1, empty inputs)
                - Suggest algorithmic approach (e.g., iteration, formula, lookup)""",
                context=""
            ),
            self.generate(
                instruction="""Analyze the problem as a DATA STRUCTURE operation.
                - Identify if inputs are lists, strings, or other collections
                - Determine operation type (filter, transform, compare, aggregate)
                - Extract patterns from input-output examples
                - Note sorting, uniqueness, or ordering requirements""",
                context=""
            ),
            self.generate(
                instruction="""Analyze the problem as a STRING/TEXT processing task.
                - Identify character-level or substring operations
                - Note case sensitivity, whitespace handling, or encoding issues
                - Extract transformation patterns from examples
                - Consider regex or slicing approaches""",
                context=""
            )
        ]
        
        interpretations = await asyncio.gather(*interpretation_tasks)
        
        # Ensemble to select best interpretation
        best_interpretation = await self.ensemble(
            instruction="""Select the most accurate problem interpretation:
            - Which analysis best explains ALL examples in the docstring?
            - Which identifies the most edge cases?
            - Which suggests the most appropriate algorithmic approach?
            - Prioritize interpretations that match the function's apparent purpose.
            Return ONLY the selected interpretation text.""",
            contexts_list=interpretations
        )

        # PHASE 2: SOLUTION DRAFTING & VALIDATION SIMULATION (Cascade with Feedback)
        # Generate initial solution based on selected interpretation
        draft_solution = await self.generate(
            instruction=f"""Generate Python function code based on this interpretation:
            {best_interpretation}
            
            STRICT REQUIREMENTS:
            - Function name MUST exactly match the ENTRY POINT
            - Return type MUST match examples (int vs float matters)
            - Handle ALL edge cases shown in examples
            - Code must be minimal - implement ONLY what's specified
            - Include no comments or explanations - only raw code
            - Use efficient algorithms appropriate to the problem type""",
            context=best_interpretation
        )

        # Simulate validation by checking against examples
        validation_analysis = await self.generate(
            instruction=f"""Critically analyze this code against the problem specification:
            {draft_solution}
            
            CHECKLIST:
            1. Does function name exactly match ENTRY POINT?
            2. Do return types match all examples? (int/float/bool/list)
            3. Are all edge cases from examples handled? (like n=1, empty lists)
            4. Is the logic consistent with the docstring examples?
            5. Are there any off-by-one errors or boundary condition mistakes?
            6. Is the code unnecessarily complex or missing key optimizations?
            
            If any issues found, describe them specifically. If perfect, say 'VALID'.""",
            context=draft_solution
        )

        # Revise if issues found
        current_solution = draft_solution
        if "VALID" not in validation_analysis.upper():
            current_solution = await self.revise(
                instruction=f"""Fix all issues identified in validation:
                {validation_analysis}
                
                REVISION REQUIREMENTS:
                - Preserve correct parts of original code
                - Fix ONLY the identified issues
                - Maintain exact function signature
                - Ensure return types match examples precisely
                - Handle all edge cases mentioned in validation
                - Return ONLY the corrected code, no explanations""",
                context=draft_solution
            )

        # PHASE 3: FINAL REFINEMENT & OUTPUT STANDARDIZATION (Iterative Polish)
        # Ensure clean, specification-compliant output
        final_code = await self.summarize(
            instruction="""Extract ONLY the Python function code from the following text.
            - Remove any explanatory text, comments, or markdown
            - Ensure function signature exactly matches ENTRY POINT
            - Preserve all logic and edge case handling
            - Return ONLY the raw Python code, nothing else""",
            context=current_solution
        )

        # One final safety check for function name matching
        entry_point_match = re.search(r'Function name:\s*(\w+)', self.problem_text)
        if entry_point_match:
            required_name = entry_point_match.group(1)
            # Ensure function definition uses correct name
            final_code = re.sub(r'def\s+\w+\s*\(', f'def {required_name}(', final_code, count=1)

        return final_code