# Workflow ID: mbppplus_143_0
# Benchmark: mbppplus
# Data Indices: [251, 75]

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

        # Step 1: Decompose the problem into core components
        decomposition = await self.decompose(
            instruction="""Break down this programming problem into essential components:
            1. Input type and structure (list, string, tuple, etc.)
            2. Output type and structure (must match input type unless specified otherwise)
            3. Transformation/filtering rule (what condition determines inclusion/exclusion?)
            4. Edge cases to consider (empty inputs, single elements, boundary values, type mismatches)
            5. Any implicit constraints (preserve order? handle duplicates? performance requirements?)
            Return as structured subproblems with clear dependencies.""",
            context=""
        )

        # Step 2: Generate multiple solution strategies in parallel
        strategy_instructions = [
            """Generate a Python solution using functional programming style (list comprehensions, filter, map).
            Prioritize readability and safety. Never modify collections while iterating.
            Handle edge cases explicitly. Preserve input type in output.""",
            
            """Generate a Python solution using explicit imperative loops (for/while with indices or safe iteration).
            Include guard clauses for edge cases. Ensure no skipped elements during filtering.
            Match input type exactly in return value.""",
            
            """Generate a Python solution using specialized methods (regex for strings, set operations for uniqueness, etc.).
            Only use if appropriate for the data type. Include necessary imports.
            Optimize for correctness over cleverness."""
        ]

        strategy_candidates = await asyncio.gather(
            *[self.generate(instruction=instr, context="") for instr in strategy_instructions]
        )

        # Step 3: Generate synthetic edge cases for validation
        edge_cases = await self.generate(
            instruction="""Generate 5-7 synthetic test cases that stress-test the solution:
            - Empty input
            - Input with all elements filtered out
            - Boundary values (0, -0, max/min values)
            - Single element cases
            - Type edge cases (if applicable)
            Format as Python assert statements.""",
            context=f"Problem decomposition: {decomposition}"
        )

        # Step 4: Validate each candidate against edge cases
        validation_tasks = []
        for i, candidate in enumerate(strategy_candidates):
            validation = await self.generate(
                instruction=f"""Critically evaluate this solution against edge cases:
                {edge_cases}
                
                Check for:
                - Runtime errors (IndexError, TypeError, etc.)
                - Logical errors (incorrect filtering, skipped elements)
                - Type mismatches (returning list when tuple expected)
                - Edge case failures
                
                Return detailed feedback and suggested fixes if any issues found.""",
                context=candidate
            )
            validation_tasks.append(validation)

        validations = await asyncio.gather(*validation_tasks)

        # Step 5: Revise candidates based on validation feedback
        revised_candidates = []
        for i, (candidate, validation) in enumerate(zip(strategy_candidates, validations)):
            if "error" in validation.lower() or "fail" in validation.lower() or "issue" in validation.lower():
                revised = await self.revise(
                    instruction=f"""Fix all issues identified in validation:
                    {validation}
                    
                    Requirements:
                    - Maintain original solution's core approach
                    - Handle all edge cases explicitly
                    - Preserve input type in output
                    - Use defensive programming
                    - Keep code clean and readable""",
                    context=candidate
                )
                revised_candidates.append(revised)
            else:
                revised_candidates.append(candidate)

        # Step 6: Ensemble - select or synthesize best solution
        final_solution = await self.ensemble(
            instruction="""Select the most robust, efficient, and readable solution.
            Criteria:
            1. Correctness (passes all edge cases)
            2. Type safety (preserves input type)
            3. Readability and Pythonic style
            4. Efficiency (appropriate for problem scale)
            5. Minimal dependencies
            
            If no single solution is perfect, synthesize elements from multiple candidates.
            Return ONLY the final Python function implementation with necessary imports.""",
            contexts_list=revised_candidates
        )

        # Step 7: Final hardening and cleanup
        hardened_solution = await self.revise(
            instruction="""Final cleanup and hardening:
            - Ensure function signature matches exactly what's required
            - Add necessary imports at top (only if used)
            - Use descriptive variable names
            - Remove any debug prints or comments
            - Verify return type matches input type
            - Optimize for clarity and maintainability
            
            Return ONLY the cleaned Python code, nothing else.""",
            context=final_solution
        )

        return hardened_solution