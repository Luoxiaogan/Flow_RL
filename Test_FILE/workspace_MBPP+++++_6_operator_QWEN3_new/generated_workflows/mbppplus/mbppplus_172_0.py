# Workflow ID: mbppplus_172_0
# Benchmark: mbppplus
# Data Indices: [144, 186]

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
        """
        Universal workflow for programming problem domain with adaptive strategy selection
        and rigorous validation for edge cases and type consistency.
        """
        import asyncio
        import re
        import math
        from typing import List, Dict, Any

        # Phase 1: Deep Problem Analysis
        problem_analysis = await self.generate(
            instruction="""Perform comprehensive analysis of this programming problem:
            1. CLASSIFICATION: Is this primarily a mathematical, string manipulation, data structure, or logical problem?
            2. INPUT CHARACTERISTICS: What are the expected input types, ranges, and potential edge cases (empty inputs, single elements, boundaries)?
            3. OUTPUT REQUIREMENTS: What exact data type should be returned (list, tuple, set, string, etc.)? Is order preservation important?
            4. KEY OPERATIONS: What core algorithms or operations are needed (searching, filtering, pattern matching, arithmetic, etc.)?
            5. CONSTRAINTS: Are there any explicit or implicit constraints mentioned or implied?
            6. FAILURE MODES: What are the most likely points of failure (type errors, division by zero, index out of bounds, etc.)?
            7. TEST CASE INSIGHTS: What can be inferred from the basic test cases about expected behavior?
            Provide structured analysis covering all these points in detail.""",
            context=""
        )

        # Phase 2: Parallel Strategy Generation
        # Generate multiple solution approaches simultaneously
        strategy_tasks = [
            self.generate(
                instruction=f"""Based on this analysis: {problem_analysis}
                Develop a MATHEMATICAL/NUMERICAL solution strategy:
                - Focus on arithmetic operations, number theory, and computational efficiency
                - Explicitly handle edge cases like zero, negative numbers, and boundaries
                - Ensure type consistency in returns
                - Consider algorithmic complexity
                Provide detailed step-by-step approach with code structure outline.""",
                context=problem_analysis
            ),
            self.generate(
                instruction=f"""Based on this analysis: {problem_analysis}
                Develop a STRING/TEXT processing solution strategy:
                - Focus on pattern matching, parsing, and text manipulation
                - Consider regex patterns, string methods, and character-level operations
                - Handle edge cases like empty strings, single characters, and special characters
                - Ensure proper encoding and type handling
                Provide detailed step-by-step approach with code structure outline.""",
                context=problem_analysis
            ),
            self.generate(
                instruction=f"""Based on this analysis: {problem_analysis}
                Develop a DATA STRUCTURE/LOGICAL solution strategy:
                - Focus on collections (lists, sets, tuples), searching, filtering, and transformations
                - Consider time/space complexity trade-offs
                - Handle edge cases like empty collections, duplicates, and order preservation
                - Ensure proper type conversions and returns
                Provide detailed step-by-step approach with code structure outline.""",
                context=problem_analysis
            )
        ]
        
        # Execute strategies in parallel
        strategy_results = await asyncio.gather(*strategy_tasks)
        
        # Phase 3: Strategy Synthesis
        synthesized_strategy = await self.ensemble(
            instruction="""Synthesize the best elements from all three strategies into a unified implementation plan:
            1. Identify the most robust approach for the core problem based on problem classification
            2. Incorporate edge case handling from all strategies, particularly for empty inputs and boundary conditions
            3. Ensure type consistency and proper return format as specified in problem analysis
            4. Combine efficiency considerations from mathematical approach with clarity from data structure approach
            5. If string operations are needed, integrate the most precise pattern matching techniques
            6. Create a comprehensive implementation plan that addresses all potential failure modes identified in analysis
            7. The final plan should be detailed enough for direct code implementation with clear function structure
            Prioritize solutions that are both correct and readable, with explicit handling of all edge cases.""",
            contexts_list=strategy_results
        )

        # Phase 4: Code Implementation
        initial_implementation = await self.programmer(
            instruction=f"""Implement a Python function based on this synthesized strategy: {synthesized_strategy}
            CRITICAL REQUIREMENTS:
            - Handle ALL edge cases identified in analysis (empty inputs, single elements, boundaries, etc.)
            - Return EXACTLY the data type specified in problem analysis
            - Include comprehensive input validation
            - Ensure type consistency throughout (no unexpected type conversions)
            - Code must be readable and maintainable with clear variable names
            - Include comments for complex logic sections
            - Follow Python best practices and PEP 8 guidelines
            - The function signature must match exactly what's required in the problem
            Generate the complete implementation with all necessary imports included in the code block.""",
            context=synthesized_strategy
        )

        # Phase 5: Validation and Refinement Loop
        refined_implementation = initial_implementation
        max_revisions = 3
        revision_count = 0
        
        while revision_count < max_revisions:
            validation_feedback = await self.generate(
                instruction=f"""Critically review this implementation for the following:
                1. EDGE CASE COVERAGE: Does it properly handle empty inputs, single elements, and boundary conditions?
                2. TYPE CONSISTENCY: Are all inputs/outputs the correct types? Any unexpected conversions?
                3. ERROR HANDLING: Are there potential runtime errors (division by zero, index errors, etc.)?
                4. EFFICIENCY: Any obvious performance bottlenecks or unnecessarily complex operations?
                5. READABILITY: Is the code clear, well-structured, and properly commented?
                6. REQUIREMENT COMPLIANCE: Does it match the exact function signature and return type required?
                7. ROBUSTNESS: Would it pass extensive test suites with edge cases?
                If no significant issues found, respond with 'VALIDATED'. Otherwise, provide specific, actionable revision instructions.""",
                context=refined_implementation
            )
            
            if "VALIDATED" in validation_feedback.upper():
                break
                
            # Revise based on feedback
            refined_implementation = await self.revise(
                instruction=f"""Revise this code based on the following feedback: {validation_feedback}
                CRITICAL: Maintain all correct functionality while addressing the identified issues.
                Ensure revisions don't introduce new bugs or break existing edge case handling.
                Preserve the exact function signature and return type.
                Improve code clarity and add comments where helpful.
                The revision must be more robust than the previous version.""",
                context=refined_implementation
            )
            
            revision_count += 1

        # Phase 6: Final Output Extraction
        # Extract just the code implementation (assuming programmer returns code in markdown code block)
        final_code = refined_implementation
        if "