# Workflow ID: mbppplus_18_0
# Benchmark: mbppplus
# Data Indices: [279, 85, 284]

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

        # Step 1: Meta-classification - Understand problem essence
        problem_analysis = await self.generate(
            instruction="""Perform deep structural analysis of this programming problem:
            1. Classify by computational type: mathematical, data transformation, logical validation, or hybrid
            2. Identify key operations needed: arithmetic, iteration, comparison, mapping, etc.
            3. Extract all constraints: input types, output format, edge cases (empty, single, duplicates, boundaries)
            4. Hypothesize potential failure modes and tricky edge cases
            5. Note any implicit requirements from test cases or examples
            Format as structured analysis with clear sections.""",
            context=""
        )

        # Step 2: Parallel solution generation from three perspectives
        math_approach, data_approach, logic_approach = await asyncio.gather(
            self.generate(
                instruction=f"""Develop solution using mathematical/formulaic reasoning:
                - Focus on deriving equations, formulas, or algebraic relationships
                - Consider numerical edge cases (zero, negative, overflow)
                - Reference this analysis: {problem_analysis}
                - Output should be pseudocode or clear step-by-step logic""",
                context=problem_analysis
            ),
            self.generate(
                instruction=f"""Develop solution using data structure/algorithmic reasoning:
                - Focus on appropriate data structures (lists, dicts, sets) and algorithms
                - Consider iteration patterns, lookups, and transformations
                - Handle edge cases like empty inputs, single elements, duplicates
                - Reference this analysis: {problem_analysis}
                - Output should be pseudocode or clear step-by-step logic""",
                context=problem_analysis
            ),
            self.generate(
                instruction=f"""Develop solution using logical/conditional reasoning:
                - Focus on decision trees, conditionals, and state transitions
                - Consider all possible branches and edge conditions
                - Reference this analysis: {problem_analysis}
                - Output should be pseudocode or clear step-by-step logic""",
                context=problem_analysis
            )
        )

        # Step 3: Synthesize best solution from parallel approaches
        synthesized_solution = await self.ensemble(
            instruction="""Synthesize a unified, optimal solution from these three approaches:
            1. Compare all three solutions for correctness, completeness, and edge case handling
            2. Resolve any contradictions by referring back to problem requirements
            3. Combine the strongest elements from each approach
            4. Ensure the solution handles all identified edge cases
            5. Output should be clear, step-by-step pseudocode ready for implementation""",
            contexts_list=[math_approach, data_approach, logic_approach]
        )

        # Step 4: Convert to precise Python implementation
        python_implementation = await self.revise(
            instruction=f"""Convert this pseudocode into exact Python implementation:
            - MUST use the exact function name and parameters from the original problem
            - MUST return the exact data type specified (string, list, dict, etc.)
            - Handle all edge cases identified in analysis: {problem_analysis}
            - Include necessary imports at top of function if needed
            - Code must be clean, efficient, and readable
            - DO NOT include any explanations or comments - only the function code
            - Ensure output matches required format exactly (e.g., string representation of dict)""",
            context=synthesized_solution
        )

        # Step 5: Validation and refinement loop (max 2 iterations)
        final_code = python_implementation
        for i in range(2):
            validation = await self.generate(
                instruction=f"""Critically validate this code:
                1. Does it handle all edge cases from analysis: {problem_analysis}?
                2. Does it match exact function signature and return type?
                3. Are there any type mismatches or logical errors?
                4. Is the code efficient and clean?
                If no issues, respond 'VALID'. Otherwise, list specific issues to fix.""",
                context=final_code
            )
            
            if "VALID" in validation.upper() and "ISSUE" not in validation.upper():
                break
            else:
                final_code = await self.revise(
                    instruction=f"""Fix these specific issues: {validation}
                    While preserving correct functionality and exact function signature.
                    Reference original problem requirements and edge cases: {problem_analysis}""",
                    context=final_code
                )

        return final_code