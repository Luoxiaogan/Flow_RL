# Workflow ID: mbppplus_16_0
# Benchmark: mbppplus
# Data Indices: [23, 178]

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
        self.programmer = operator.Programmer(self.llm, self.problem_text)
        self.decompose = operator.Decompose(self.llm, self.problem_text)

    async def run_workflow(self):
        import asyncio
        import re
        import json
        from collections import defaultdict

        # Phase 1: Comprehensive problem analysis
        problem_analysis = await self.generate(
            instruction="""Perform deep analysis of this programming problem:
            1. Examine the function signature to understand input/output types
            2. Analyze test cases to infer the transformation rule
            3. Identify edge cases that should be handled (empty inputs, single elements, etc.)
            4. Determine if this is a simple transformation, aggregation, or complex algorithm
            5. Note any type conversion requirements (list to tuple, etc.)
            6. Identify if order preservation is important
            7. Determine if duplicates should be handled specially
            8. Extract the exact return type expected from test cases
            
            Provide structured analysis covering all these points.""",
            context=""
        )

        # Phase 2: Problem classification and strategy selection
        classification = await self.generate(
            instruction=f"""Based on this analysis:
            {problem_analysis}
            
            Classify this problem into one of these categories:
            A. SIMPLE TRANSFORMATION: Element-wise operation (like string.upper())
            B. AGGREGATION: Counting, grouping, or summarizing elements
            C. COMPLEX ALGORITHM: Multi-step processing or custom logic
            
            Also determine:
            - Primary data types involved
            - Required output type
            - Key edge cases to handle
            - Any special considerations (order, duplicates, etc.)
            
            Respond in JSON format with keys: category, data_types, output_type, edge_cases, special_considerations""",
            context=problem_analysis
        )

        # Phase 3: Generate implementation based on classification
        if "SIMPLE TRANSFORMATION" in classification or "A." in classification:
            implementation_strategy = """Implement a straightforward transformation function.
            Key requirements:
            - Handle the specific transformation shown in test cases
            - Preserve input type where appropriate
            - Handle edge cases: empty strings, single characters, mixed case
            - Return exactly the type shown in test cases
            - Keep implementation simple and direct
            """
        elif "AGGREGATION" in classification or "B." in classification:
            implementation_strategy = """Implement an aggregation function that counts or groups elements.
            Key requirements:
            - Convert unhashable types (like lists) to hashable ones (like tuples) if needed
            - Use appropriate data structures (dict, Counter, etc.)
            - Handle edge cases: empty inputs, single elements, duplicates
            - Return exactly the type shown in test cases
            - Ensure correct counting logic
            """
        else:  # COMPLEX ALGORITHM
            implementation_strategy = """Implement a more complex algorithmic solution.
            Key requirements:
            - Break down the problem into logical steps
            - Handle all edge cases identified in analysis
            - Use appropriate data structures and algorithms
            - Return exactly the type shown in test cases
            - Ensure efficiency and correctness
            """

        # Generate initial implementation
        initial_implementation = await self.programmer(
            instruction=f"""Generate Python code for this problem based on the analysis and classification.
            
            Problem Analysis:
            {problem_analysis}
            
            Classification:
            {classification}
            
            Implementation Strategy:
            {implementation_strategy}
            
            CRITICAL REQUIREMENTS:
            - Use EXACT function name from signature
            - Include all necessary imports
            - Handle ALL identified edge cases
            - Return EXACTLY the type shown in test cases
            - Code must be clean, efficient, and readable
            - Do NOT wrap in any outer function or class
            
            Generate only the function implementation as specified.""",
            context=classification
        )

        # Phase 4: Validation and refinement
        validation = await self.generate(
            instruction=f"""Critically review this implementation:
            {initial_implementation}
            
            Check for:
            1. Correctness against test cases
            2. Proper edge case handling
            3. Correct return types
            4. Efficiency and readability
            5. Potential bugs or logical errors
            6. Type consistency
            
            If any issues are found, provide specific revision instructions.
            If implementation is perfect, respond with "APPROVED".""",
            context=initial_implementation
        )

        final_implementation = initial_implementation
        if "APPROVED" not in validation.upper():
            # Revise implementation based on feedback
            final_implementation = await self.revise(
                instruction=f"""Revise the implementation based on this feedback:
                {validation}
                
                Ensure:
                - All issues are addressed
                - Code remains clean and efficient
                - Function signature is preserved
                - Return types are correct
                - Edge cases are properly handled
                
                Generate only the revised function implementation.""",
                context=initial_implementation
            )

        # Phase 5: Final verification and output
        final_check = await self.generate(
            instruction=f"""Perform final verification of this implementation:
            {final_implementation}
            
            Confirm:
            1. Function name matches exactly
            2. All imports are included
            3. Return type matches requirements
            4. Edge cases are handled
            5. Code is clean and follows best practices
            
            If any final adjustments needed, specify them clearly.
            Otherwise, respond with "FINAL APPROVED".""",
            context=final_implementation
        )

        if "FINAL APPROVED" not in final_check.upper():
            # One final revision if needed
            final_implementation = await self.revise(
                instruction=f"""Make final adjustments based on:
                {final_check}
                
                Generate only the final function implementation.""",
                context=final_implementation
            )

        return final_implementation