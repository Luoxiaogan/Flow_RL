# Workflow ID: mbppplus_77_0
# Benchmark: mbppplus
# Data Indices: [298, 148]

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

        # PHASE 1: Problem Specification Extraction
        specification = await self.generate(
            instruction="""Thoroughly analyze the programming problem and extract a detailed specification. Your analysis must include:
            1. Function signature and expected return type (list, tuple, set, bool, int, etc.)
            2. Description of what the function should accomplish in plain English
            3. List of edge cases to handle (empty inputs, single elements, duplicates, negative numbers, type conversions, etc.)
            4. Any constraints on order preservation, mutability, or performance
            5. Expected behavior for boundary conditions
            6. Common pitfalls or mistakes to avoid based on the problem description
            7. Type handling requirements (e.g., string to int conversion, preserving tuple vs list)
            Format this as a structured markdown document with clear sections.""",
            context=""
        )

        # PHASE 2: Parallel Solution Generation
        solution_attempts = await asyncio.gather(
            self.generate(
                instruction=f"""Generate a Python function implementation based on the following specification:
                {specification}
                
                Approach 1: Focus on simplicity and readability. Use straightforward logic even if not the most efficient.
                Include comments explaining key steps. Handle all edge cases mentioned in the specification.""",
                context=specification
            ),
            self.generate(
                instruction=f"""Generate a Python function implementation based on the following specification:
                {specification}
                
                Approach 2: Focus on robustness and edge case handling. Explicitly check for and handle all edge cases.
                Use defensive programming techniques. Prioritize correctness over elegance.""",
                context=specification
            ),
            self.generate(
                instruction=f"""Generate a Python function implementation based on the following specification:
                {specification}
                
                Approach 3: Focus on efficiency and Pythonic style. Use built-in functions, comprehensions, and idiomatic Python.
                Avoid unnecessary variables or steps. Still ensure all edge cases are handled correctly.""",
                context=specification
            )
        )

        # PHASE 3: Parallel Solution Critique and Refinement
        refined_solutions = []
        for i, solution in enumerate(solution_attempts):
            refined = await self.revise(
                instruction=f"""Critically review and improve the following code solution:
                
                {solution}
                
                Review Criteria:
                1. Does it match the function signature and return type specified?
                2. Does it handle all edge cases listed in the specification?
                3. Are there any logical errors or off-by-one mistakes?
                4. Is the code type-safe? (e.g., converting strings to numbers when needed)
                5. Does it preserve order if required? Handle duplicates correctly?
                6. Is there any redundant or unnecessary code that can be removed?
                7. Fix any syntax errors or Python anti-patterns.
                
                Return only the corrected and improved Python function code, nothing else.""",
                context=solution
            )
            refined_solutions.append(refined)

        # PHASE 4: Ensemble Selection
        final_code = await self.ensemble(
            instruction="""Select the best solution from the candidates below. Criteria for selection:
            1. Correctness: Must handle all edge cases and match specification
            2. Robustness: Least likely to fail on unseen test cases
            3. Clarity: Code is readable and maintainable
            4. Efficiency: Reasonably efficient without sacrificing correctness
            5. Type Safety: Properly handles data types as specified
            
            Return ONLY the selected Python function code, with no additional text or explanation.""",
            contexts_list=refined_solutions
        )

        # PHASE 5: Validation and Final Revision (if needed)
        # Check for obvious errors in final code
        if "SyntaxError" in final_code or "NameError" in final_code or "IndentationError" in final_code:
            final_code = await self.revise(
                instruction="""The code contains syntax or structural errors. Fix all Python syntax errors, 
                indentation issues, and undefined variable references. Return only the corrected Python function.""",
                context=final_code
            )

        # Ensure it's just the function code (remove any explanatory text)
        # Extract code block if present
        code_match = re.search(r'