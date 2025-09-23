# Workflow ID: mbppplus_38_0
# Benchmark: mbppplus
# Data Indices: [119, 114, 275]

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
        Universal workflow for programming problem-solving domain.
        Handles any problem by classifying, generating strategies, hardening against edge cases,
        and validating synthetically.
        """
        import asyncio
        import re

        # Stage 1: Extract specification and classify problem
        problem_profile = await self.generate(
            instruction="""Analyze the problem and create a structured profile including:
            1. Input types and structures (e.g., tuple, string, int)
            2. Output type and structure requirements
            3. Core operation category: 
               - Data structure transformation (e.g., tuple/list/dict operations)
               - String parsing and conversion
               - Mathematical computation (e.g., LCM, GCD, sequences)
               - Logical validation or comparison
            4. Key constraints and edge cases to consider (empty inputs, single elements, negatives, duplicates, etc.)
            5. Any implicit requirements from function signature or problem description
            Format as a clear, bullet-pointed analysis.""",
            context=""
        )

        # Stage 2: Generate multiple implementation strategies in parallel
        strategy_tasks = [
            self.generate(
                instruction=f"""Generate a Python function implementation based on this problem profile:
                {problem_profile}
                
                Strategy 1: Direct and straightforward approach. Prioritize clarity and simplicity.
                Include detailed comments explaining each step.
                Handle edge cases explicitly.""",
                context=""
            ),
            self.generate(
                instruction=f"""Generate a Python function implementation based on this problem profile:
                {problem_profile}
                
                Strategy 2: Optimized and efficient approach. Use built-in functions or libraries where appropriate.
                Focus on performance and minimal operations.
                Still handle all edge cases.""",
                context=""
            ),
            self.generate(
                instruction=f"""Generate a Python function implementation based on this problem profile:
                {problem_profile}
                
                Strategy 3: Defensive and robust approach. Add explicit type checks and error handling.
                Prioritize correctness over brevity. Document assumptions.
                Handle all conceivable edge cases, even if not explicitly mentioned.""",
                context=""
            )
        ]
        
        strategy_candidates = await asyncio.gather(*strategy_tasks)

        # Stage 3: Ensemble best strategy
        selected_solution = await self.ensemble(
            instruction="""Select the best solution from the candidates based on:
            1. Correctness: Does it satisfy the problem specification?
            2. Robustness: Does it handle edge cases comprehensively?
            3. Pythonic style: Is it clean, readable, and follows Python conventions?
            4. Efficiency: Is it reasonably efficient without premature optimization?
            5. Type safety: Does it return exactly the required type?
            
            Return ONLY the selected solution code, with no additional text or markdown.
            Do NOT wrap in