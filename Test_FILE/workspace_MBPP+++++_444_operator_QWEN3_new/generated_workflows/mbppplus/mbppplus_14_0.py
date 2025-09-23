# Workflow ID: mbppplus_14_0
# Benchmark: mbppplus
# Data Indices: [184, 72, 128]

import asyncio

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

        # Stage 1: Problem Classification & Intent Extraction
        classification = await self.generate(
            instruction="""Thoroughly analyze the problem to determine:
            1. Primary category: Is this a string parsing, list/tuple operation, mathematical computation, or logic/validation problem?
            2. Input types: What data types are expected as inputs? (e.g., string, list of ints, tuple of strings)
            3. Output type: What should the function return? (e.g., integer, tuple, list)
            4. Key operations: What transformations or computations are required? (e.g., parsing, summing, filtering)
            5. Edge cases: What boundary conditions must be handled? (e.g., empty inputs, single elements, malformed strings)
            6. Constraints: Are there any implicit restrictions? (e.g., no external libraries, preserve order, handle duplicates)
            Provide a structured analysis that will guide solution strategy generation.""",
            context=""
        )

        # Stage 2: Generate Multiple Solution Strategies
        strategy_instructions = [
            """Based on the problem classification, develop a STRATEGY-FIRST solution:
            - Begin by outlining the high-level approach before writing code
            - Favor readability and explicit steps over clever one-liners
            - Include comments explaining key decisions
            - Handle all identified edge cases explicitly
            - Ensure return type matches exactly what's expected""",
            
            """Based on the problem classification, develop a FUNCTIONAL-FIRST solution:
            - Use map/filter/reduce patterns where appropriate
            - Leverage comprehensions and built-in functions
            - Minimize state mutation
            - Still handle all edge cases and match return type
            - Prioritize conciseness without sacrificing clarity""",
            
            """Based on the problem classification, develop a DEFENSIVE-FIRST solution:
            - Include input validation and error handling
            - Use type hints in thinking (even if not in final code)
            - Consider malformed inputs and graceful degradation
            - Add assertions or sanity checks in the implementation logic
            - Ensure robustness over elegance"""
        ]

        # Generate strategies in parallel
        strategy_contexts = [classification] * 3
        strategy_results = await asyncio.gather(*[
            self.generate(instruction=strategy_instructions[i], context=strategy_contexts[i])
            for i in range(3)
        ])

        # Stage 3: Draft Full Code Implementations
        code_draft_instructions = [
            f"""Convert this strategy into a complete, runnable Python function:
            Strategy: {strategy_results[0]}
            
            Requirements:
            - Use EXACT function signature from problem
            - Include necessary imports INSIDE the function if needed
            - Return correct data type (list vs tuple vs int etc.)
            - Handle ALL edge cases identified in classification
            - Code must be syntactically valid and follow PEP8
            - NO explanations or markdown - only raw code
            - If parsing strings, handle whitespace and formatting variations""",
            
            f"""Convert this strategy into a complete, runnable Python function:
            Strategy: {strategy_results[1]}
            
            Requirements:
            - Use EXACT function signature from problem
            - Include necessary imports INSIDE the function if needed
            - Return correct data type (list vs tuple vs int etc.)
            - Handle ALL edge cases identified in classification
            - Code must be syntactically valid and follow PEP8
            - NO explanations or markdown - only raw code
            - Optimize for functional purity where possible""",
            
            f"""Convert this strategy into a complete, runnable Python function:
            Strategy: {strategy_results[2]}
            
            Requirements:
            - Use EXACT function signature from problem
            - Include necessary imports INSIDE the function if needed
            - Return correct data type (list vs tuple vs int etc.)
            - Handle ALL edge cases identified in classification
            - Code must be syntactically valid and follow PEP8
            - NO explanations or markdown - only raw code
            - Include defensive checks for input validity"""
        ]

        code_drafts = await asyncio.gather(*[
            self.generate(instruction=code_draft_instructions[i], context=strategy_results[i])
            for i in range(3)
        ])

        # Stage 4: Validate and Revise Each Draft
        validation_instructions = [
            """Critically review this code draft:
            1. Does it match the EXACT function signature required?
            2. Does it handle ALL edge cases from classification? (empty inputs, single elements, malformed data)
            3. Is the return type correct? (list vs tuple vs int)
            4. Are there any syntax errors or logical flaws?
            5. Could it fail on any reasonable input? What inputs would break it?
            6. Is it unnecessarily complex or could it be simplified?
            
            REVISE the code to fix all identified issues. Return ONLY the corrected code with no explanations.
            Preserve the original approach but make it robust and correct.""",
            
            """Critically review this code draft:
            1. Does it match the EXACT function signature required?
            2. Does it handle ALL edge cases from classification? (empty inputs, single elements, malformed data)
            3. Is the return type correct? (list vs tuple vs int)
            4. Are there any syntax errors or logical flaws?
            5. Could it fail on any reasonable input? What inputs would break it?
            6. Is it unnecessarily complex or could it be simplified?
            
            REVISE the code to fix all identified issues. Return ONLY the corrected code with no explanations.
            Preserve the original approach but make it robust and correct.""",
            
            """Critically review this code draft:
            1. Does it match the EXACT function signature required?
            2. Does it handle ALL edge cases from classification? (empty inputs, single elements, malformed data)
            3. Is the return type correct? (list vs tuple vs int)
            4. Are there any syntax errors or logical flaws?
            5. Could it fail on any reasonable input? What inputs would break it?
            6. Is it unnecessarily complex or could it be simplified?
            
            REVISE the code to fix all identified issues. Return ONLY the corrected code with no explanations.
            Preserve the original approach but make it robust and correct."""
        ]

        revised_codes = await asyncio.gather(*[
            self.revise(instruction=validation_instructions[i], context=code_drafts[i])
            for i in range(3)
        ])

        # Stage 5: Ensemble - Select or Synthesize Best Solution
        final_solution = await self.ensemble(
            instruction="""You are given three candidate solutions for the same problem.
            Evaluate them based on:
            1. Correctness: Which handles edge cases most comprehensively?
            2. Robustness: Which is least likely to fail on unexpected inputs?
            3. Clarity: Which has the most readable and maintainable logic?
            4. Precision: Which matches the expected return type and signature exactly?
            5. Efficiency: Which has the most appropriate complexity for the task?
            
            SELECT the single best solution. If two solutions are complementary (e.g., one has better edge case handling, another has cleaner core logic), SYNTHESIZE them by combining the best parts.
            
            Return ONLY the final code with no explanations, markdown, or additional text.
            Ensure imports are inside the function if needed, and signature is exact.""",
            contexts_list=revised_codes
        )

        # Stage 6: Final Polish - Enforce Format and Extract Code Block
        polished_code = await self.revise(
            instruction="""Final quality check:
            1. Ensure this is ONLY Python code with no markdown, explanations, or formatting
            2. Verify function signature matches EXACTLY what was required
            3. Confirm all necessary imports are INSIDE the function if used
            4. Remove any print statements, debug code, or extra comments
            5. Ensure return type is correct (list vs tuple vs int etc.)
            6. Trim any leading/trailing whitespace or newlines
            
            Return ONLY the clean, final code ready for execution.""",
            context=final_solution
        )

        return polished_code