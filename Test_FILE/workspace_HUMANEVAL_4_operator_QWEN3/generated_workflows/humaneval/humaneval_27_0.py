# Workflow ID: humaneval_27_0
# Benchmark: humaneval
# Data Indices: [133, 28]

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
        Universal workflow for specification-driven Python function generation.
        Handles any problem in the domain by decomposing, drafting, validating,
        and refining code based on docstring examples and ENTRY POINT.
        """
        import asyncio
        import re

        # Step 1: Decompose problem and extract transformation logic
        decomposition = await self.generate(
            instruction="""Thoroughly analyze the function specification and examples.
            Identify:
            1. Input type and structure (list, string, numbers, etc.)
            2. Output type and format (int, float, string, etc.)
            3. Core operations (mathematical, string, list processing)
            4. Edge cases (empty inputs, zeros, negatives, type boundaries)
            5. Any implicit constraints (rounding, ceiling, flooring, etc.)
            6. Required imports (math, etc.) based on operations
            Present findings in structured bullet points.""",
            context=""
        )

        # Step 2: Conditional branching based on problem type
        # Generate two parallel solution drafts for robustness
        draft_tasks = [
            self.generate(
                instruction=f"""Based on this analysis:
                {decomposition}

                Write the minimal Python function that satisfies the specification.
                - Use the exact ENTRY POINT function name.
                - Match return types precisely (int vs float matters).
                - Handle all edge cases identified.
                - Do NOT include imports — they will be added later.
                - Return only the function body as code, no explanations.
                Focus on literal interpretation of examples.""",
                context=decomposition
            ),
            self.generate(
                instruction=f"""Based on this analysis:
                {decomposition}

                Write the minimal Python function that satisfies the specification.
                - Use the exact ENTRY POINT function name.
                - Match return types precisely.
                - Generalize from examples to abstract rule.
                - Do NOT include imports.
                - Return only the function body as code.
                Focus on inferring the underlying algorithm.""",
                context=decomposition
            )
        ]

        # Step 3: Generate drafts in parallel
        draft1, draft2 = await asyncio.gather(*draft_tasks)

        # Step 4: Ensemble to select or merge best solution
        final_draft = await self.ensemble(
            instruction="""Select the best solution between the two drafts.
            Criteria:
            1. Correctness: Must satisfy all examples in the docstring.
            2. Minimalism: No extra logic, features, or defensive code.
            3. Precision: Exact return types, correct function name.
            4. Edge case handling: Must cover all identified edge cases.
            If both are valid, merge their strengths. Return only the code.""",
            contexts_list=[draft1, draft2]
        )

        # Step 5: Validate and refine against examples
        refined = await self.revise(
            instruction=f"""Critically validate this code against the docstring examples:
            - Simulate each example step by step.
            - Verify input/output matches exactly.
            - Check return type precision (int vs float).
            - Ensure function name matches ENTRY POINT.
            - Add missing edge case handling if needed.
            - Remove any unnecessary code.
            Return the corrected, minimal function body.""",
            context=final_draft
        )

        # Step 6: Detect and inject required imports
        # Look for keywords that imply imports
        import_lines = []
        if "math.ceil" in refined or "math.floor" in refined or "math" in decomposition.lower():
            import_lines.append("import math")
        if "json" in refined or "json" in decomposition.lower():
            import_lines.append("import json")
        if "re" in refined or "regex" in decomposition.lower():
            import_lines.append("import re")

        # Inject imports at the top of the function body
        if import_lines:
            final_code = "\n".join(import_lines) + "\n" + refined
        else:
            final_code = refined

        # Step 7: Final sanitization — ensure clean, minimal code
        sanitized = await self.revise(
            instruction="""Final cleanup:
            - Ensure code contains ONLY the function definition and necessary imports.
            - Remove any comments, print statements, or debug code.
            - Verify function name matches ENTRY POINT exactly.
            - Ensure no extra whitespace or formatting.
            Return the pristine code block.""",
            context=final_code
        )

        return sanitized