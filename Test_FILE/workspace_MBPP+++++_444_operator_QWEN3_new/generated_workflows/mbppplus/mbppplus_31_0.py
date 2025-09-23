# Workflow ID: mbppplus_31_0
# Benchmark: mbppplus
# Data Indices: [170, 112, 90]

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

        # Step 1: Problem Analysis and Classification
        analysis = await self.generate(
            instruction="""Thoroughly analyze the problem statement and classify it into one of these categories:
            1. Syntax Validation (e.g., bracket matching, expression validation)
            2. Logical Validation (e.g., all elements satisfy a condition, boolean checks)
            3. Structural Transformation (e.g., grouping, mapping, aggregating data)
            
            Also identify:
            - Input data type (string, tuple, list, etc.)
            - Expected output type and format
            - Key operations or constraints mentioned
            - Any edge cases implied (empty inputs, single elements, boundaries)
            - Confidence level in your classification (1-10 scale)
            
            Structure your response clearly with headings for each category.""",
            context=""
        )

        # Step 2: Extract confidence and decide strategy depth
        confidence_check = await self.generate(
            instruction="""From the following analysis, extract only the confidence score (a number between 1-10):
            If no explicit score is given, infer it based on the clarity and specificity of the classification.
            Respond with ONLY the number, nothing else.""",
            context=analysis
        )
        
        try:
            confidence = int(confidence_check.strip())
        except:
            confidence = 5  # default medium confidence

        # Step 3: Strategy Selection - Parallel candidates for low confidence, targeted for high
        if confidence < 7:
            # Generate multiple candidate approaches in parallel
            candidate_instructions = [
                """Based on the problem analysis, generate a solution using a stack-based or iterative approach. 
                Focus on explicit step-by-step logic, handling edge cases like empty inputs and malformed sequences.
                Include necessary imports inside the function. Match the exact function signature from the problem.""",
                
                """Based on the problem analysis, generate a solution using functional programming constructs (map, filter, reduce, any, all).
                Focus on concise, declarative logic. Handle edge cases explicitly. Include necessary imports inside the function.
                Match the exact function signature from the problem.""",
                
                """Based on the problem analysis, generate a solution using dictionary or set operations for grouping or membership testing.
                Focus on data structure efficiency. Handle edge cases explicitly. Include necessary imports inside the function.
                Match the exact function signature from the problem."""
            ]
            
            candidates = await asyncio.gather(
                *[self.generate(instruction=instr, context=analysis) for instr in candidate_instructions]
            )
            
            # Ensemble: Select or synthesize the best candidate
            solution_draft = await self.ensemble(
                instruction="""Evaluate each candidate solution for:
                1. Correctness (does it logically solve the problem?)
                2. Robustness (does it handle edge cases: empty, single element, boundaries?)
                3. Efficiency (is it unnecessarily complex?)
                4. Adherence to signature and return type
                
                Select the best candidate or synthesize a new version combining the strongest elements.
                Return ONLY the selected or synthesized solution code, nothing else.""",
                contexts_list=candidates
            )
        else:
            # High confidence - generate targeted solution
            solution_draft = await self.generate(
                instruction=f"""Generate a precise solution based on this analysis:
                {analysis}
                
                Instructions:
                - Use the most appropriate algorithm for the classified category
                - Handle all edge cases explicitly (empty inputs, single elements, boundaries)
                - Include necessary imports inside the function
                - Match the exact function signature and return type
                - Write clean, readable code with clear variable names
                - Return ONLY the function implementation, no extra text""",
                context=analysis
            )

        # Step 4: Revision with edge case simulation
        refined_solution = await self.revise(
            instruction="""Critically examine this solution:
            1. Mentally simulate its behavior on these edge cases: empty input, single element input, maximum/minimum boundary values, malformed input
            2. Check for type consistency (return type must match exactly)
            3. Verify that all imports are inside the function
            4. Ensure no extra text or comments are included
            5. Optimize for clarity and efficiency
            
            Rewrite the solution to fix any identified issues. Return ONLY the corrected function implementation.""",
            context=solution_draft
        )

        # Step 5: Final formatting and compliance check
        final_solution = await self.generate(
            instruction="""Format this solution to meet EXACT requirements:
            - Include ONLY the function implementation
            - All necessary imports must be inside the function
            - Use the EXACT function name and parameter names from the original problem
            - Return the appropriate data type as shown in test cases
            - NO extra text, comments, or wrappers
            
            If any requirement is not met, fix it. Return ONLY the corrected code.""",
            context=refined_solution
        )

        return final_solution