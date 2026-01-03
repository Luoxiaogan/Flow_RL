# Workflow ID: mbppplus_39_0
# Benchmark: mbppplus
# Data Indices: [312, 245]

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
        import json

        # Step 1: Classify problem type and extract key constraints
        classification = await self.generate(
            instruction="""Thoroughly analyze the programming problem and classify it by:
            1. Primary domain: string manipulation, numerical computation, data structure (list/tuple/set), or logical validation.
            2. Key operations: sorting, searching, pattern matching, arithmetic, set operations, etc.
            3. Edge cases: empty inputs, single elements, duplicates, negative numbers, type boundaries.
            4. Return type: must match exactly (list vs tuple vs set vs bool vs int).
            5. Order sensitivity: does output order matter?
            6. Performance constraints: is efficiency critical?
            Provide structured JSON with keys: domain, operations, edge_cases, return_type, order_sensitive, efficiency_critical.""",
            context=""
        )

        # Step 2: Decompose into subproblems if complex
        decomposition = await self.decompose(
            instruction="""Break this problem into minimal, testable subproblems. Each subproblem should:
            - Be independently solvable
            - Have clear input/output
            - Cover one logical step
            - Include validation criteria
            Return as list of subproblem dicts with 'id', 'description', 'dependencies'.""",
            context=classification
        )

        # Step 3: Generate multiple solution strategies in parallel
        strategy_instructions = [
            """Generate a solution using direct algorithmic approach (loops, conditionals). 
            Prioritize readability and explicit edge case handling. Include type checks and input validation.
            Return ONLY the function implementation with necessary imports inside the function body.
            Match the exact function signature and return type specified in the problem.""",
            
            """Generate a solution using built-in Python functions and data structures (set operations, comprehensions, sorted, etc.).
            Optimize for conciseness and Pythonic style. Still handle all edge cases.
            Return ONLY the function implementation with necessary imports inside the function body.
            Match the exact function signature and return type specified in the problem.""",
            
            """Generate a solution using mathematical or regex-based approach where applicable.
            Focus on correctness and boundary condition coverage.
            Return ONLY the function implementation with necessary imports inside the function body.
            Match the exact function signature and return type specified in the problem."""
        ]

        candidate_solutions = await asyncio.gather(
            *[self.programmer(instruction=instr, context=classification) for instr in strategy_instructions]
        )

        # Step 4: Revise each candidate to inject robustness
        robust_solutions = []
        for i, candidate in enumerate(candidate_solutions):
            robust = await self.revise(
                instruction=f"""Improve this solution by:
                1. Adding explicit handling for all edge cases mentioned in classification: {classification}
                2. Ensuring return type matches exactly (list/tuple/set/bool/int as required)
                3. Adding input validation and type safety
                4. Preserving order if required
                5. Including comments for complex logic
                6. Removing any unnecessary code or imports
                Return ONLY the improved function implementation with imports inside the function body.
                Maintain the exact function signature.""",
                context=candidate
            )
            robust_solutions.append(robust)

        # Step 5: Ensemble - select best solution based on robustness, clarity, and correctness
        final_solution = await self.ensemble(
            instruction="""Select the single best solution from the candidates based on:
            1. Correctness: handles all edge cases and matches return type
            2. Robustness: includes input validation and error prevention
            3. Readability: clear variable names, logical flow, helpful comments
            4. Efficiency: appropriate algorithmic complexity
            5. Conciseness: no redundant code
            Return ONLY the selected function implementation with imports inside the function body.
            Preserve the exact function signature and return type.""",
            contexts_list=robust_solutions
        )

        # Step 6: Final validation and cleanup
        cleaned_solution = await self.revise(
            instruction="""Final cleanup: 
            1. Ensure ONLY the function implementation is returned (no extra text, markdown, or explanations)
            2. Verify all necessary imports are inside the function body
            3. Confirm function signature matches exactly (parameter names, order)
            4. Remove any debug prints or test code
            5. Ensure return type is correct
            Return ONLY the clean, production-ready function implementation.""",
            context=final_solution
        )

        return cleaned_solution