# Workflow ID: humaneval_16_0
# Benchmark: humaneval
# Data Indices: [136, 16]

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
        Universal code generation workflow that reverse-engineers specifications from examples.
        Uses Diamond Pattern with Feedback Cascade for robust, generalizable solutions.
        """
        import asyncio

        # PHASE 1: PARALLEL ANALYSIS FORKS
        # Extract behavioral patterns, edge cases, and type/structure requirements simultaneously
        pattern_analysis, edge_analysis, type_analysis = await asyncio.gather(
            self.generate(
                instruction="""Analyze the provided examples to infer the core transformation rule.
                - What is the mathematical, logical, or string operation being performed?
                - How do inputs map to outputs? Derive the underlying function, not just describe examples.
                - Ignore variable names; focus on operations and conditions.
                - Express the rule as a generalizable algorithm in plain English.
                Example: "Filter list for negative numbers, take maximum; filter for positives, take minimum; return as tuple with None for empty sets."""",
                context=""
            ),
            self.generate(
                instruction="""Identify all edge cases and boundary conditions from examples and problem description.
                - What inputs trigger special behavior? (empty, zero, single element, all same, etc.)
                - What values are explicitly excluded? (e.g., zero in integer problems)
                - What are the failure modes? (type errors, index errors, etc.)
                - List each edge case with its expected output and why it's handled that way.
                Format: "Edge Case: [description] → Expected: [output] because [reason]".""",
                context=""
            ),
            self.generate(
                instruction="""Infer exact return type, structure, and constraints from examples.
                - What is the precise return type? (int, float, tuple, list, etc.)
                - Are there type conversions or normalizations? (e.g., case folding, int vs float)
                - What is the data structure? (tuple order, list length, dict keys)
                - Are there implicit constraints? (e.g., ignore zeros, distinct only)
                - Summarize as: "Return: [type] with [structure] where [constraints]".""",
                context=""
            )
        )

        # PHASE 2: SYNTHESIZE UNIFIED SPECIFICATION
        unified_spec = await self.ensemble(
            instruction="""Synthesize a complete, unambiguous specification from the three analyses.
            - Combine pattern rules, edge cases, and type/structure into one coherent document.
            - Resolve any conflicts (e.g., if pattern says "include zero" but edge case says "exclude").
            - Prioritize example-derived behavior over descriptive text.
            - Format as:
              SPECIFICATION:
              1. Core Rule: [general algorithm]
              2. Edge Cases: [list with outputs]
              3. Return Contract: [type, structure, constraints]
            This spec will be used to generate code — it must be exhaustive and precise.""",
            contexts_list=[pattern_analysis, edge_analysis, type_analysis]
        )

        # PHASE 3: GENERATE INITIAL IMPLEMENTATION
        initial_code = await self.generate(
            instruction=f"""Generate Python code that strictly implements the following specification:
            {unified_spec}

            Requirements:
            - Function name must exactly match ENTRY POINT.
            - Return type and structure must match spec exactly.
            - Handle all edge cases explicitly.
            - Use clear, minimal logic — no over-engineering.
            - Include no comments or docstrings — only function definition.
            - Assume no external libraries unless mathematically essential.

            Example output format:
            def function_name(arg):
                # implementation
                return result""",
            context=unified_spec
        )

        # PHASE 4: VALIDATE AND REVISE AGAINST EDGE CASES
        revised_code = await self.revise(
            instruction=f"""Critique and improve this code against the edge cases and return contract:
            Edge Cases to Validate:
            {edge_analysis}

            Return Contract:
            {type_analysis}

            Check for:
            - Missing edge case handling
            - Type mismatches (int vs float, None handling)
            - Structural errors (wrong tuple order, list vs scalar)
            - Logical gaps (e.g., not filtering correctly)
            - Overcomplication — simplify if possible

            Return only the corrected function code with no additional text.""",
            context=initial_code
        )

        # PHASE 5: FINAL SANITY CHECK (Optional second revision for conciseness)
        final_code = await self.revise(
            instruction="""Final polish: Ensure code is minimal, readable, and exactly matches specification.
            - Remove any redundant operations
            - Use built-ins where appropriate (e.g., min/max, set, filter)
            - Verify function name matches ENTRY POINT exactly
            - Return only the function code — no explanations, comments, or docstrings.""",
            context=revised_code
        )

        return final_code