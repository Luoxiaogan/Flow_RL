# Workflow ID: humaneval_78_0
# Benchmark: humaneval
# Data Indices: [152, 29]

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
        Universal workflow for code generation from specifications.
        Handles any problem in the domain by inductively inferring patterns from examples.
        """
        import asyncio
        import re

        # Step 1: Parallel extraction of key components
        example_extraction, pattern_analysis, constraint_identification = await asyncio.gather(
            self.generate(
                instruction="""Extract all input-output examples from the docstring.
                Format each as:
                Input: [args]
                Output: [expected result]
                Ensure you capture ALL examples, including edge cases.
                If no explicit examples, note that and proceed with specification analysis.""",
                context=""
            ),
            self.generate(
                instruction="""Analyze the functional pattern:
                - What is the relationship between inputs and outputs?
                - Is it element-wise, aggregate, conditional, or recursive?
                - What operations are likely involved (math, string, list, etc.)?
                - Are there hidden constraints or edge cases?
                Provide a structured hypothesis.""",
                context=""
            ),
            self.generate(
                instruction="""Identify hard constraints:
                - Function name (MUST match ENTRY POINT exactly)
                - Return type (int, float, list, etc. — must match examples)
                - Parameter types and counts
                - Any explicit or implicit edge cases
                Format as bullet points.""",
                context=""
            )
        )

        # Step 2: Synthesize unified understanding
        problem_understanding = await self.ensemble(
            instruction="""Synthesize the extracted examples, pattern analysis, and constraints into a unified problem specification.
            Prioritize:
            1. Exact function signature requirements
            2. Input-output transformation rules
            3. Edge case handling
            4. Return type precision
            Output a concise, structured summary that captures all critical information for code generation.""",
            contexts_list=[example_extraction, pattern_analysis, constraint_identification]
        )

        # Step 3: Generate multiple solution hypotheses in parallel
        solution_hypotheses = await asyncio.gather(
            self.generate(
                instruction=f"""Generate Python code based on this understanding:
                {problem_understanding}
                
                Requirements:
                - Use EXACT function name from ENTRY POINT
                - Match return types precisely (int vs float matters)
                - Handle all edge cases identified
                - Prefer list comprehensions or built-in functions when appropriate
                - Return code ONLY — no explanations, no imports (they'll be auto-added)
                
                Start with the most straightforward implementation.""",
                context=problem_understanding
            ),
            self.generate(
                instruction=f"""Generate an ALTERNATIVE Python implementation:
                {problem_understanding}
                
                Requirements:
                - Same function name and return type
                - Use a different approach (e.g., for-loop instead of comprehension, or vice versa)
                - Explicitly handle edge cases with conditionals if needed
                - Return code ONLY — no explanations
                
                This is a fallback in case the first solution is too complex or fails.""",
                context=problem_understanding
            )
        )

        # Step 4: Validate and refine solutions
        refined_solutions = []
        for i, solution in enumerate(solution_hypotheses):
            # First revision: fix syntax and adherence to spec
            refined = await self.revise(
                instruction=f"""Revise this code to ensure:
                1. Function name EXACTLY matches ENTRY POINT
                2. Return type matches examples (int/float/list/etc.)
                3. No missing edge case handling
                4. Clean, minimal Python (no unnecessary variables or steps)
                5. Correct use of built-ins (zip, map, filter, etc.) if applicable
                
                If any issue is found, fix it. Return ONLY the revised code.""",
                context=solution
            )
            # Second revision: simulate test case validation
            validated = await self.revise(
                instruction=f"""Imagine running this code against the provided examples.
                Would it produce the exact expected outputs?
                If not, fix the logic. Pay special attention to:
                - Element-wise vs aggregate operations
                - Absolute values, string methods, or other transformations
                - Empty list/string edge cases
                - Type mismatches (int vs float)
                
                Return ONLY the final, validated code.""",
                context=refined
            )
            refined_solutions.append(validated)

        # Step 5: Select best solution
        final_solution = await self.ensemble(
            instruction="""Select the BEST solution based on:
            1. Correctness (must handle all examples and edge cases)
            2. Simplicity (prefer list comprehensions and built-ins)
            3. Readability (clear, Pythonic code)
            4. Robustness (handles edge cases explicitly if needed)
            
            If both are equally good, pick the first one.
            Return ONLY the selected code — nothing else.""",
            contexts_list=refined_solutions
        )

        return final_solution