# Workflow ID: mbpp_0_0
# Benchmark: mbpp
# Data Indices: [1, 0]

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
        Implement the core problem-solving logic here.
        Remember: 
        - ALL operators return STRINGS
        - Import modules (json, re, etc.) at the beginning
        - Use detailed, comprehensive instructions
        - Parse JSON with json.loads() if needed
        """
        import asyncio
        # import json  # Uncomment if you need JSON parsing
        # import re    # Uncomment if you need regex
        
        # Step 1: Extract function name from test cases
        func_name = await self.generate(
            instruction="Extract only the function name from the test cases. Return ONLY the function name, nothing else.",
            context=""
        )
        
        # Step 2: Generate initial solution with comprehensive instructions
        code = await self.generate(
            instruction=f"""
            Write a Python function named '{func_name}' that solves this task.
            Requirements:
            1. Include ALL necessary import statements at the top (e.g., from collections import Counter)
            2. Handle edge cases: empty string, None input, single character
            3. Return ONLY the executable Python code, no explanations or markdown formatting
            4. Follow best practices: clear variable names, comments where helpful, efficient logic
            5. Match the exact signature expected by the test cases
            """,
            context=""
        )
        
        # Step 3: Revise for correctness and completeness
        final_code = await self.revise(
            instruction="""
            Check the following code for:
            - Missing imports (e.g., math, re, collections, etc.)
            - Edge case handling (empty inputs, None, boundary values)
            - Logical errors (e.g., off-by-one indexing, incorrect return types)
            Fix any issues found. Return ONLY the corrected code, no explanations.
            """,
            context=code
        )
        
        return final_code