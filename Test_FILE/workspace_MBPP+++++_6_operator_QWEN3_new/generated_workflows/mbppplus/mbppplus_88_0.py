# Workflow ID: mbppplus_88_0
# Benchmark: mbppplus
# Data Indices: [138, 255]

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

        # Step 1: Classify the problem type to determine strategy
        classification = await self.generate(
            instruction="""Analyze this programming problem and classify it by solution approach:
            - Is it primarily mathematical (closed-form formula, direct computation)?
            - Is it algorithmic (requires loops, state tracking, data structure manipulation)?
            - Is it string/text processing?
            - Does it involve combinatorics or optimization?
            - Are there obvious edge cases (empty input, single element, negatives, duplicates)?
            
            Also determine:
            - Expected input/output types
            - Whether order matters
            - If duplicates should be handled specially
            - Time/space complexity constraints (if any)
            
            Return a structured classification in plain text.""",
            context=""
        )

        # Step 2: Conditional branching based on classification
        is_mathematical = "mathematical" in classification.lower() or "formula" in classification.lower()
        is_simple = "direct" in classification.lower() or "one-liner" in classification.lower()

        if is_mathematical and is_simple:
            # Direct path for simple mathematical problems
            code_attempt = await self.programmer(
                instruction=f"""Generate a Python function that solves this mathematical problem.
                Classification context: {classification}
                
                Requirements:
                - Use exact function signature from problem
                - Include necessary imports inside function
                - Handle edge cases mentioned in classification
                - Return correct data type
                - Output ONLY the function code, nothing else
                
                Focus on precision and correctness. Consider floating point issues if applicable.""",
                context=classification,
                max_retries=3
            )
            
            # Clean and format the output
            final_code = await self.revise(
                instruction="""Ensure the code meets EXACT output requirements:
                - Only function implementation, no extra text
                - Imports inside function
                - Exact function name and parameters
                - No wrapping in classes or outer functions
                - Return type matches problem specification
                - Remove any markdown code block markers if present""",
                context=code_attempt
            )
            
            return final_code

        else:
            # Parallel generation of multiple solution approaches
            solution_sketches = await asyncio.gather(
                self.generate(
                    instruction=f"""Develop a detailed solution sketch for this problem.
                    Classification: {classification}
                    
                    Approach 1: Brute force or straightforward simulation.
                    - Describe step by step logic
                    - Identify key variables and data structures
                    - Handle edge cases explicitly
                    - Consider time/space complexity""",
                    context=classification
                ),
                self.generate(
                    instruction=f"""Develop a detailed solution sketch for this problem.
                    Classification: {classification}
                    
                    Approach 2: Optimized or mathematical insight.
                    - Look for patterns or formulas
                    - Consider preprocessing or cumulative arrays
                    - Use efficient data structures
                    - Handle edge cases explicitly""",
                    context=classification
                ),
                self.generate(
                    instruction=f"""Develop a detailed solution sketch for this problem.
                    Classification: {classification}
                    
                    Approach 3: Alternative strategy (e.g., two pointers, greedy, DP).
                    - Different perspective from above
                    - Focus on robustness and edge cases
                    - Consider input validation
                    - Handle boundary conditions""",
                    context=classification
                )
            )

            # Convert sketches to code in parallel
            code_attempts = await asyncio.gather(
                *[self.programmer(
                    instruction=f"""Convert this solution sketch into working Python code:
                    {sketch}
                    
                    Requirements:
                    - Use exact function signature from problem
                    - Include necessary imports inside function
                    - Handle all edge cases mentioned
                    - Return correct data type
                    - Output ONLY the function code, nothing else""",
                    context=sketch,
                    max_retries=2
                ) for sketch in solution_sketches]
            )

            # Ensemble to select and synthesize best solution
            best_code = await self.ensemble(
                instruction=f"""Evaluate these code solutions and select the best one:
                Criteria:
                1. Correctness (handles edge cases, matches expected behavior)
                2. Efficiency (optimal time/space complexity)
                3. Readability and maintainability
                4. Robustness (input validation, error handling)
                
                If multiple solutions have strengths, synthesize a hybrid solution.
                Output ONLY the final code, nothing else.
                
                Classification context: {classification}""",
                contexts_list=code_attempts
            )

            # Final formatting and validation pass
            final_code = await self.revise(
                instruction="""Strictly enforce output format requirements:
                - ONLY the function implementation, no explanations
                - Imports must be inside the function
                - Exact function name and parameters as specified
                - No wrapping in classes or outer functions
                - Return type must match problem specification
                - Remove any markdown, comments, or extra text
                - Ensure code is syntactically correct""",
                context=best_code
            )

            # Validation loop - up to 2 retries if code is malformed
            for attempt in range(2):
                if "def " in final_code and not final_code.startswith("