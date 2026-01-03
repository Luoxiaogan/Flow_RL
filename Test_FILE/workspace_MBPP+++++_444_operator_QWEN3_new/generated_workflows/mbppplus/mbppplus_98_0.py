# Workflow ID: mbppplus_98_0
# Benchmark: mbppplus
# Data Indices: [152, 145, 126]

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
        import math

        # STEP 1: CLASSIFY THE PROBLEM TYPE AND EXTRACT KEY CONSTRAINTS
        classification = await self.generate(
            instruction="""Thoroughly analyze the programming problem and provide a structured classification including:
            1. Primary category: Is this a mathematical computation, string manipulation, list/tuple operation, or logical validation problem?
            2. Key operations needed: What core Python operations or algorithms are required? (e.g., sorting, regex, arithmetic, filtering)
            3. Critical edge cases: What edge cases must be handled? (e.g., empty inputs, invalid values, boundary conditions)
            4. Return type requirements: What exact data type must be returned? (list, tuple, None, float, etc.)
            5. Required imports: What modules (if any) are needed? (e.g., re, math)
            6. Constraints: Any explicit or implicit constraints mentioned or implied?
            Format your response as a clear, labeled breakdown.""",
            context=""
        )

        # STEP 2: GENERATE MULTIPLE SOLUTION STRATEGIES IN PARALLEL
        solution_strategies = [
            "Implement the most straightforward, readable approach using built-in Python functions.",
            "Implement an optimized or alternative approach (e.g., regex vs manual iteration, math.pi vs 22/7).",
            "Implement a defensive, edge-case-first approach that explicitly handles all boundary conditions before main logic."
        ]

        solution_attempts = await asyncio.gather(
            *[self.generate(
                instruction=f"""Based on this classification:
                {classification}

                {strategy} 
                
                IMPORTANT:
                - Match the exact function signature from the problem.
                - Handle all edge cases identified in classification.
                - Return the exact required data type.
                - Include necessary imports INSIDE the function if needed.
                - Do NOT wrap in any outer function or class.
                - Return ONLY the function implementation in this format: