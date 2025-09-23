# Workflow ID: mbppplus_13_0
# Benchmark: mbppplus
# Data Indices: [3, 174]

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

        # Phase 1: Parallel Problem Analysis
        task_analysis, classification, edge_case_analysis = await asyncio.gather(
            self.generate(
                instruction="""Analyze the core task:
                1. What is the function supposed to do? Extract the exact transformation or computation.
                2. What are the input and output types? Be specific (list, tuple, string, etc.).
                3. Are there any explicit constraints or conditions mentioned?
                4. Format your response as a structured summary with clear sections.""",
                context=""
            ),
            self.generate(
                instruction="""Classify the problem type and recommend strategy:
                Categories: [String Manipulation, List/Tuple Operations, Mathematical, Logic/Validation, Data Structure Algorithm]
                For each category, explain why it fits or doesn't fit.
                Then recommend the most suitable solution approach:
                - Direct transformation (e.g., split/reverse/join for strings)
                - Iterative validation (e.g., checking index parity)
                - Mathematical formula
                - Set operations
                - Recursive or functional approach
                Justify your recommendation with specific references to the problem text.""",
                context=""
            ),
            self.generate(
                instruction="""Anticipate edge cases and failure modes:
                Consider:
                - Empty inputs
                - Single-element inputs
                - Boundary values (0, negative numbers, max/min)
                - Type mismatches
                - Duplicates
                - Order preservation requirements
                - Performance constraints
                List at least 5 potential edge cases and explain how they might break a naive solution.
                Format as a numbered list with explanations.""",
                context=""
            )
        )

        # Phase 2: Synthesize Analysis into Unified Plan
        unified_plan = await self.ensemble(
            instruction="""Synthesize the three analyses into a single, coherent implementation plan:
            1. Start with the recommended strategy from the classification.
            2. Incorporate edge case handling from the edge case analysis.
            3. Ensure type consistency and signature matching from the task analysis.
            4. Structure the plan as:
               - Step 1: Input validation and edge case handling
               - Step 2: Core algorithm/transformations
               - Step 3: Output formatting and type conversion
            Be explicit about variable names, loop structures, and Python idioms to use.""",
            contexts_list=[task_analysis, classification, edge_case_analysis]
        )

        # Phase 3: Conditional Routing Based on Problem Type
        problem_type = await self.generate(
            instruction=f"""Based on the classification and unified plan, extract the dominant problem type.
            Return ONLY one of these exact strings:
            "String Manipulation", "List/Tuple Operations", "Mathematical", "Logic/Validation", "Data Structure Algorithm"
            Classification context: {classification}""",
            context=classification
        )

        # Generate initial code based on problem type
        if "String Manipulation" in problem_type:
            code_attempt = await self.generate(
                instruction=f"""Generate Python code for a string manipulation problem.
                Plan: {unified_plan}
                Edge cases to handle: {edge_case_analysis}
                Requirements:
                - Use functional transformations where possible (split, join, map, etc.)
                - Handle empty strings and single words
                - Preserve whitespace rules as specified
                - Return exact type specified in signature
                Generate ONLY the function implementation with necessary imports inside the function.
                No explanations, no markdown, no extra text.""",
                context=unified_plan
            )
        elif "Logic/Validation" in problem_type:
            code_attempt = await self.generate(
                instruction=f"""Generate Python code for a logic/validation problem.
                Plan: {unified_plan}
                Edge cases to handle: {edge_case_analysis}
                Requirements:
                - Use explicit loops with index tracking if needed
                - Include comprehensive condition checks
                - Handle empty and single-element cases
                - Return boolean or specified type
                Generate ONLY the function implementation with necessary imports inside the function.
                No explanations, no markdown, no extra text.""",
                context=unified_plan
            )
        else:
            # Fallback: Generate multiple approaches and ensemble
            approaches = await asyncio.gather(
                self.generate(
                    instruction=f"""Generate Approach 1: Direct and simple implementation.
                    Plan: {unified_plan}
                    Focus on readability and simplicity.
                    Generate ONLY the function implementation.""",
                    context=unified_plan
                ),
                self.generate(
                    instruction=f"""Generate Approach 2: Defensive and robust implementation.
                    Plan: {unified_plan}
                    Edge cases: {edge_case_analysis}
                    Focus on handling all edge cases explicitly.
                    Generate ONLY the function implementation.""",
                    context=unified_plan
                ),
                self.generate(
                    instruction=f"""Generate Approach 3: Optimized and idiomatic implementation.
                    Plan: {unified_plan}
                    Focus on Pythonic patterns and efficiency.
                    Generate ONLY the function implementation.""",
                    context=unified_plan
                )
            )
            code_attempt = await self.ensemble(
                instruction="""Select the best implementation:
                Criteria:
                1. Correctness (handles edge cases)
                2. Simplicity and readability
                3. Adherence to problem requirements
                4. Pythonic style
                Return ONLY the selected code implementation, nothing else.""",
                contexts_list=approaches
            )

        # Phase 4: Validation and Iterative Refinement
        final_code = code_attempt
        for iteration in range(3):
            validation_result = await self.programmer(
                instruction=f"""Test the code against the visible test cases.
                If it fails, identify exactly why and what needs to be fixed.
                If it passes, return 'VALID'.
                Code to test:
                {final_code}""",
                context=final_code,
                max_retries=1
            )
            
            if "VALID" in validation_result:
                break
            else:
                final_code = await self.revise(
                    instruction=f"""Revise the code to fix the issues identified in validation:
                    Validation feedback: {validation_result}
                    Original plan: {unified_plan}
                    Edge cases: {edge_case_analysis}
                    Requirements:
                    - Maintain correct function signature
                    - Handle all edge cases
                    - Return correct data type
                    Generate ONLY the revised function implementation, nothing else.""",
                    context=final_code
                )

        # Phase 5: Final Formatting and Output
        final_output = await self.revise(
            instruction="""Ensure the code meets all output requirements:
            - ONLY the function implementation
            - EXACT function name from reference
            - All imports inside the function
            - Preserve function signatures including parameter names
            - NO outer function or class wrappers
            - Return appropriate data types
            If any of these are violated, fix them. Otherwise, return the code unchanged.
            Return ONLY the code, no explanations.""",
            context=final_code
        )

        return final_output