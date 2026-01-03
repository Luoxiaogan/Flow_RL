# Workflow ID: mbppplus_6_0
# Benchmark: mbppplus
# Data Indices: [190, 226]

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

        # Phase 1: Decompose and Classify
        decomposition = await self.decompose(
            instruction="""Break down this programming problem into core components:
            1. Identify input data types and structures (list, tuple, string, etc.)
            2. Determine expected output type and format
            3. List potential edge cases (empty inputs, single elements, duplicates, nested structures, boundary values)
            4. Classify problem type: list/tuple ops, string manipulation, math computation, data structure algorithm, or logic problem
            5. Extract any explicit or implicit constraints (order preservation, type consistency, performance hints)
            Return as structured subproblems with clear dependencies.""",
            context=""
        )

        classification = await self.generate(
            instruction=f"""Based on this decomposition:
            {decomposition}
            
            Provide a concise classification including:
            - Primary category (list, string, math, data structure, logic)
            - Critical constraints (e.g., 'must return tuple', 'preserve order', 'handle empty input')
            - Key edge cases to handle
            - Recommended solution strategy (iterative, functional, recursive, etc.)
            Format as bullet points for clarity.""",
            context=str(decomposition)
        )

        # Phase 2: Parallel Solution Generation
        solution_instructions = [
            """Generate a minimalist, direct solution that mirrors reference examples.
            Focus on simplicity and clarity. Assume basic edge cases are handled unless specified otherwise.
            Prioritize readability over defensive programming.""",
            
            """Generate a defensive, robust solution that explicitly handles all edge cases.
            Include guards for empty inputs, type checks, and boundary conditions.
            Prioritize correctness over elegance. Use explicit conditionals if needed.""",
            
            """Generate a functional/declarative solution using comprehensions, built-ins, and immutable patterns.
            Avoid explicit loops where possible. Leverage Python's functional features.
            Ensure type consistency and order preservation as required."""
        ]

        candidate_solutions = await asyncio.gather(
            *[self.generate(
                instruction=f"""{instr}

                Problem Classification:
                {classification}

                Generate ONLY the function implementation as specified in the problem.
                Include necessary imports. Match exact function signature. Return correct data type.
                Do NOT include test cases, explanations, or markdown.""",
                context=classification
            ) for instr in solution_instructions]
        )

        # Phase 3: Iterative Validation & Revision
        revised_solutions = []
        for candidate in candidate_solutions:
            current = candidate
            for iteration in range(2):  # Max 2 revision passes
                validation = await self.revise(
                    instruction=f"""Critically validate this code against the problem requirements:

                    Problem Classification:
                    {classification}

                    Check for:
                    - Correct function signature and return type
                    - Handling of all edge cases mentioned in classification
                    - Type consistency (list vs tuple vs set)
                    - Order preservation if required
                    - Empty input handling
                    - Duplicate element handling if relevant

                    If any issues found, revise the code to fix them. Otherwise, return unchanged.
                    Return ONLY the revised (or unchanged) function implementation.""",
                    context=current
                )
                if validation.strip() == current.strip():
                    break  # No changes needed
                current = validation
            revised_solutions.append(current)

        # Phase 4: Ensemble Synthesis
        final_solution = await self.ensemble(
            instruction=f"""Synthesize the best possible solution from these candidates:

            Problem Classification:
            {classification}

            Evaluation Criteria:
            1. Correctness: Must handle all edge cases and constraints
            2. Robustness: Graceful handling of unexpected inputs
            3. Efficiency: Avoid unnecessary complexity
            4. Readability: Clear, maintainable code
            5. Type Consistency: Match expected return types exactly

            Combine strengths from each candidate:
            - Take simplicity from minimalist version
            - Take edge case handling from defensive version
            - Take elegance from functional version

            Return ONLY the synthesized function implementation.""",
            contexts_list=revised_solutions
        )

        # Phase 5: Final Meta-Validation
        ultimate_solution = await self.revise(
            instruction=f"""Perform final meta-validation:

            Problem Classification:
            {classification}

            Imagine you are the test suite maintainer. What hidden edge cases might still break this code?
            Common pitfalls to check:
            - Empty inputs (lists, tuples, strings)
            - Single element cases
            - Nested structures (if applicable)
            - Type mismatches (returning list when tuple expected)
            - Order preservation requirements
            - Duplicate handling

            If any vulnerabilities found, add minimal guards or fixes.
            Otherwise, return unchanged.

            Return ONLY the final function implementation.""",
            context=final_solution
        )

        return ultimate_solution