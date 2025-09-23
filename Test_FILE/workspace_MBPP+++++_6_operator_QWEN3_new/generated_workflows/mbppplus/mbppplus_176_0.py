# Workflow ID: mbppplus_176_0
# Benchmark: mbppplus
# Data Indices: [232, 67]

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
        from typing import List, Dict, Any

        # Step 1: Classify problem type and extract key constraints
        classification = await self.generate(
            instruction="""Perform deep problem classification:
            1. Identify primary domain: string manipulation, list/tuple operations, mathematical computation, data structure algorithm, or logic problem.
            2. Extract exact function signature including parameter names and expected return type.
            3. Infer implicit constraints: mutability, order preservation, duplication handling, edge cases (empty inputs, single elements, type boundaries).
            4. Determine solution paradigm: direct implementation, regex/library use, algorithmic decomposition, or stateful processing.
            5. List potential edge cases not explicitly mentioned but logically implied.
            Format as structured JSON with keys: domain, signature, constraints, paradigm, edge_cases.""",
            context=""
        )

        # Step 2: Generate three parallel solution strategies
        solution_strategies = await asyncio.gather(
            self.generate(
                instruction=f"""Generate Solution Strategy 1 (Direct Implementation):
                Based on classification: {classification}
                - Use basic loops and conditionals
                - Avoid external libraries
                - Prioritize readability and explicit logic
                - Handle all inferred edge cases
                - Return exact expected type (list vs tuple vs set)""",
                context=""
            ),
            self.generate(
                instruction=f"""Generate Solution Strategy 2 (Library-Optimized):
                Based on classification: {classification}
                - Leverage Python standard libraries (re, itertools, collections, etc.)
                - Prioritize conciseness and efficiency
                - Include necessary imports in code
                - Handle edge cases through library features
                - Match exact return type specifications""",
                context=""
            ),
            self.generate(
                instruction=f"""Generate Solution Strategy 3 (Algorithmic Decomposition):
                Based on classification: {classification}
                - Break problem into minimal atomic steps
                - Solve each step independently
                - Compose final solution from sub-solutions
                - Include validation checks at each stage
                - Ensure type consistency throughout""",
                context=""
            )
        )

        # Step 3: Convert strategies to code candidates
        code_candidates = await asyncio.gather(
            *[self.programmer(
                instruction=f"""Implement this strategy with rigorous edge case handling:
                Strategy: {strategy}
                Classification: {classification}
                Requirements:
                - Exact function signature as specified
                - Include ALL necessary imports at top
                - Return correct data type (list/tuple/set)
                - Handle empty inputs, single elements, duplicates
                - No wrapper functions or classes
                - Code must be production-ready and pass hidden test cases""",
                context=strategy
            ) for strategy in solution_strategies]
        )

        # Step 4: Validate and critique each candidate
        critiques = await asyncio.gather(
            *[self.revise(
                instruction=f"""Critique this code for robustness and correctness:
                - Check for edge case vulnerabilities (empty inputs, type mismatches, boundary conditions)
                - Verify return type matches specification
                - Identify potential performance bottlenecks
                - Flag any assumptions not grounded in problem statement
                - Suggest specific improvements
                Return structured critique with sections: vulnerabilities, type_compliance, performance, assumptions, improvements.""",
                context=candidate
            ) for candidate in code_candidates]
        )

        # Step 5: Revise candidates based on critiques
        revised_candidates = await asyncio.gather(
            *[self.revise(
                instruction=f"""Revise code based on this critique:
                Critique: {critique}
                Original Code: {candidate}
                Requirements:
                - Fix all identified vulnerabilities
                - Ensure type consistency
                - Optimize performance if needed
                - Maintain exact function signature
                - Preserve core logic while improving robustness""",
                context=candidate
            ) for candidate, critique in zip(code_candidates, critiques)]
        )

        # Step 6: Ensemble final selection
        final_code = await self.ensemble(
            instruction="""Select the optimal solution from these candidates:
            Criteria:
            1. Correctness: Must handle all edge cases and type requirements
            2. Robustness: Minimal assumptions, defensive programming
            3. Readability: Clear variable names, logical flow
            4. Efficiency: Reasonable time/space complexity
            5. Conciseness: Avoid unnecessary complexity
            Return ONLY the selected code implementation - no explanations, no markdown, no additional text.
            The code must be ready for immediate execution with correct imports and function signature.""",
            contexts_list=revised_candidates
        )

        # Step 7: Final validation and type checking
        validated_code = await self.revise(
            instruction="""Final validation pass:
            - Ensure code contains ONLY the function implementation
            - Verify imports are present and correct
            - Confirm function name and parameters match exactly
            - Check that return type is explicitly correct (list/tuple/set)
            - Remove any explanatory comments or markdown
            - Output must be pure executable Python code""",
            context=final_code
        )

        return validated_code