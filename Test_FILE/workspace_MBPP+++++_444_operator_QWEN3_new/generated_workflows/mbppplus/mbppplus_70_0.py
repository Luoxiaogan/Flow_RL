# Workflow ID: mbppplus_70_0
# Benchmark: mbppplus
# Data Indices: [194, 266, 240]

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
        import json

        # Step 1: Deep problem analysis - understand intent, data structures, edge cases
        analysis = await self.generate(
            instruction="""Perform deep semantic analysis of this programming problem:
            1. Identify the core task: Is it filtering, counting, transforming, comparing, or conditional logic?
            2. Extract key data structures: What types are inputs/outputs? (lists, dicts, tuples, primitives)
            3. Infer hidden constraints: Are there edge cases? (empty inputs, duplicates, boundary values)
            4. Hypothesize solution strategies: What algorithms or patterns might apply? (sorting, iteration, recursion, math)
            5. Predict potential pitfalls: Type mismatches? Off-by-one errors? Semantic misunderstandings?
            Output structured JSON with keys: task_type, data_structures, constraints, strategies, pitfalls""",
            context=""
        )

        # Step 2: Generate representative test cases from problem description
        test_cases = await self.generate(
            instruction=f"""Based on the problem description and analysis below, generate 5 comprehensive test cases:
            Analysis: {analysis}
            
            Requirements:
            - Include normal cases, edge cases (empty, single element, duplicates), and boundary conditions
            - Format as Python assert statements
            - Cover different data types and sizes
            - Test error conditions if applicable
            Output only the assert statements, one per line""",
            context=analysis
        )

        # Step 3: Parallel solution generation - explore multiple algorithmic strategies
        solution_strategies = [
            "Implement using straightforward iteration and conditional logic. Prioritize clarity over optimization.",
            "Implement using built-in Python functions and data structures (like sorted, min, heapq). Prioritize idiomatic code.",
            "Implement using mathematical or algorithmic optimizations (like early termination, space-time tradeoffs). Prioritize efficiency."
        ]

        solution_attempts = await asyncio.gather(
            *[self.generate(
                instruction=f"""{strategy}
                - Match the exact function signature from the problem
                - Handle all edge cases mentioned in analysis
                - Return correct data type (list vs tuple vs primitive)
                - Include necessary imports inside function if needed
                - Write defensive code that won't crash on unexpected inputs
                Output ONLY the function implementation, nothing else""",
                context=analysis
            ) for strategy in solution_strategies]
        )

        # Step 4: Ensemble - select best solution based on correctness and quality
        best_solution = await self.ensemble(
            instruction=f"""Evaluate all candidate solutions against these criteria:
            1. Correctness: Does it logically solve the problem as described?
            2. Robustness: Does it handle edge cases from analysis and test cases?
            3. Type consistency: Does it return the expected data type?
            4. Readability: Is the code clear and maintainable?
            5. Efficiency: Is it reasonably optimized for the problem size?
            
            Test cases to validate against:
            {test_cases}
            
            Select the single best solution. If multiple are correct, prefer the most readable and Pythonic.
            Output ONLY the selected function implementation, nothing else""",
            contexts_list=solution_attempts
        )

        # Step 5: Validation and revision loop - up to 2 attempts
        for attempt in range(2):
            validation = await self.generate(
                instruction=f"""Critically validate this solution:
                Solution: {best_solution}
                
                Check against:
                1. Problem requirements from original description
                2. Edge cases identified in analysis: {analysis}
                3. Test cases: {test_cases}
                
                If any issues found (logic errors, type mismatches, edge case failures), describe them specifically.
                If perfect, respond with 'VALID'.
                Otherwise, list all issues concisely.""",
                context=best_solution
            )

            if "VALID" in validation.upper():
                break

            # Revise based on validation feedback
            best_solution = await self.revise(
                instruction=f"""Fix all issues identified in validation:
                Validation feedback: {validation}
                
                Requirements:
                - Preserve the core algorithm unless fundamentally flawed
                - Fix specific issues mentioned
                - Maintain correct function signature and return type
                - Keep code clean and readable
                - Add comments if logic is complex
                Output ONLY the revised function implementation""",
                context=best_solution
            )
        else:
            # Fallback: Generate conservative solution if still failing
            best_solution = await self.generate(
                instruction=f"""Generate a conservative, brute-force solution that prioritizes correctness over elegance:
                - Use simple, explicit logic
                - Handle all edge cases defensively
                - Match function signature exactly
                - Return correct data type
                - Include comprehensive error handling
                Based on original problem and this analysis: {analysis}
                Output ONLY the function implementation""",
                context=""
            )

        return best_solution