# Workflow ID: mbppplus_128_0
# Benchmark: mbppplus
# Data Indices: [179, 70]

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

        # Step 1: Deep problem analysis - extract structure, constraints, edge cases
        problem_analysis = await self.generate(
            instruction="""Perform a comprehensive semantic analysis of this programming problem. Extract:
            1. Function signature (name, parameters, expected return type)
            2. Implied data structures and their properties (lists, tuples, sets, etc.)
            3. Key operations required (mathematical, combinatorial, string-based, etc.)
            4. Edge cases to consider (empty inputs, single elements, duplicates, boundary values)
            5. Any hidden constraints or invariants (order preservation, uniqueness, mutability)
            6. Similar problem archetypes this might belong to
            Present as a structured, detailed breakdown.""",
            context=""
        )

        # Step 2: Problem classification to determine solving strategy
        problem_classification = await self.generate(
            instruction=f"""Based on the following analysis:
            {problem_analysis}
            
            Classify this problem into one or more of these categories:
            - Combinatorial/List Operations
            - Mathematical/Number Theory
            - String Manipulation
            - Bit Manipulation
            - Data Structure Algorithms
            - Logic/Validation
            - Other (specify)
            
            For each applicable category, explain why it fits and what solving strategies are most appropriate.
            Also indicate if the problem can be decomposed into subproblems and if so, how.""",
            context=problem_analysis
        )

        # Step 3: Generate multiple solution strategies in parallel
        strategy_tasks = [
            self.generate(
                instruction=f"""Develop a solution strategy focusing on MATHEMATICAL INSIGHT:
                {problem_analysis}
                {problem_classification}
                
                Derive any underlying mathematical formulas or patterns. Consider closed-form solutions,
                algebraic transformations, or number theory properties. Avoid brute force if possible.
                Outline the step-by-step mathematical reasoning that leads to the solution.""",
                context=""
            ),
            self.generate(
                instruction=f"""Develop a solution strategy focusing on ITERATIVE/BRUTE-FORCE APPROACH:
                {problem_analysis}
                {problem_classification}
                
                Design a straightforward, step-by-step algorithm that solves the problem through iteration,
                enumeration, or direct simulation. Prioritize clarity and correctness over efficiency.
                Explicitly handle all edge cases identified in the analysis.""",
                context=""
            ),
            self.generate(
                instruction=f"""Develop a solution strategy focusing on PYTHONIC/BUILTIN APPROACH:
                {problem_analysis}
                {problem_classification}
                
                Leverage Python's built-in functions, itertools, functools, or standard library modules.
                Focus on concise, idiomatic Python that uses appropriate abstractions. Consider using
                list comprehensions, generator expressions, or functional programming constructs.
                Ensure the solution is readable and follows Python best practices.""",
                context=""
            )
        ]
        
        strategy_results = await asyncio.gather(*strategy_tasks)

        # Step 4: Refine each strategy into code-ready specifications
        refined_strategies = []
        for i, strategy in enumerate(strategy_results):
            refined = await self.revise(
                instruction=f"""Refine this solution strategy into a precise code specification:
                - Must match the exact function signature from the problem
                - Must handle all edge cases identified in analysis
                - Must return the correct data type (list vs tuple vs set, etc.)
                - Must include necessary imports if any
                - Must be self-contained (no external dependencies)
                - Must be efficient and idiomatic
                
                Strategy to refine:
                {strategy}
                
                Reference analysis:
                {problem_analysis}""",
                context=strategy
            )
            refined_strategies.append(refined)

        # Step 5: Generate code implementations for each refined strategy
        code_tasks = []
        for strategy in refined_strategies:
            code_task = self.programmer(
                instruction=f"""Implement the following solution specification exactly:
                {strategy}
                
                Critical requirements:
                - Function name and parameters must match exactly
                - Return type must be precisely as expected
                - Handle edge cases (empty inputs, single elements, etc.)
                - Include necessary imports inside the function if needed
                - No wrapper code, docstrings, or test cases - only the function implementation
                - Code must be syntactically correct and logically sound""",
                context=strategy
            )
            code_tasks.append(code_task)
        
        code_results = await asyncio.gather(*code_tasks)

        # Step 6: Ensemble - select and synthesize the best solution
        final_solution = await self.ensemble(
            instruction="""Evaluate all candidate solutions and select the best one:
            Criteria:
            1. Correctness: Does it handle all edge cases? Does it match expected behavior?
            2. Efficiency: Is it reasonably efficient for the problem size?
            3. Clarity: Is the code readable and maintainable?
            4. Idiomatic: Does it use Python appropriately?
            5. Robustness: Does it handle unexpected inputs gracefully?
            
            If multiple solutions are correct, prefer the most elegant or efficient.
            If no solution is perfect, select the most promising and note any needed fixes.
            Return ONLY the raw function implementation (no explanations, no markdown).""",
            contexts_list=code_results
        )

        # Step 7: Final cleanup - ensure output matches exact format requirements
        cleaned_solution = await self.revise(
            instruction="""Ensure this code matches the EXACT required format:
            - Only the function implementation (no imports outside function, no extra text)
            - Exact function name and parameters
            - Return type matches specification
            - All necessary imports are inside the function if needed
            - No docstrings, comments, or test cases
            - Pure Python code ready for execution
            
            If any adjustments are needed, make them now.""",
            context=final_solution
        )

        return cleaned_solution