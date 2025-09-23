# Workflow ID: mbppplus_130_0
# Benchmark: mbppplus
# Data Indices: [304, 331]

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

        # Step 1: Deep structural analysis of the problem
        problem_analysis = await self.generate(
            instruction="""Perform a comprehensive analysis of this programming problem. Identify:
            1. The exact input types and expected output types (list, tuple, set, int, etc.)
            2. Key operations required (filtering, mathematical computation, string parsing, etc.)
            3. Critical edge cases (empty inputs, single elements, duplicates, type boundaries)
            4. Order preservation requirements
            5. Any hidden constraints or assumptions
            6. Similarity to reference solutions in style or approach
            Format as a structured markdown report with clear sections.""",
            context=""
        )

        # Step 2: Parallel exploration - three strategic paths
        reference_approach, adversarial_cases, decomposition_plan = await asyncio.gather(
            # Path 1: Generate solution mimicking reference style
            self.programmer(
                instruction=f"""Based on the problem analysis:
                {problem_analysis}
                
                Generate a Python function that solves the problem following the style and approach of the reference solution.
                Ensure correct function signature, type handling, and edge case coverage.
                Return ONLY the function implementation with necessary imports.""",
                context=problem_analysis
            ),
            
            # Path 2: Generate adversarial edge cases and stress tests
            self.generate(
                instruction=f"""Based on the problem analysis:
                {problem_analysis}
                
                Generate 5-7 adversarial test cases that would break a naive implementation.
                Include: empty inputs, single elements, duplicates, type mismatches, boundary values.
                Format as Python assert statements that should pass for a correct solution.""",
                context=problem_analysis
            ),
            
            # Path 3: Decompose into subproblems if complex
            self.decompose(
                instruction=f"""Based on the problem analysis:
                {problem_analysis}
                
                Break this problem into minimal, independent subproblems.
                For each subproblem, specify: what it solves, its inputs/outputs, and dependencies.
                Only decompose if the problem has clear hierarchical structure or multiple distinct operations.""",
                context=problem_analysis
            )
        )

        # Step 3: Hardened solution - incorporate adversarial cases
        hardened_solution = await self.programmer(
            instruction=f"""Improve this solution by incorporating adversarial test cases:
            Original solution: {reference_approach}
            Adversarial cases: {adversarial_cases}
            
            Requirements:
            - Must handle all adversarial cases without error
            - Must preserve exact function signature and return types
            - Must be defensively coded against edge cases
            - Return ONLY the function implementation with necessary imports""",
            context=reference_approach
        )

        # Step 4: Iterative refinement with validation focus
        current_solution = hardened_solution
        for iteration in range(3):
            critique = await self.revise(
                instruction=f"""Critically evaluate this solution:
                {current_solution}
                
                Check for:
                1. Type consistency (returning list vs tuple vs set)
                2. Edge case handling (empty, single, duplicates, boundaries)
                3. Order preservation if required
                4. Efficiency for large inputs
                5. Match to reference solution style
                6. Adherence to adversarial test cases
                
                If flaws found, provide specific, actionable fixes.
                If no flaws, respond with 'VALIDATED'.""",
                context=current_solution
            )
            
            if "VALIDATED" in critique.upper():
                break
                
            current_solution = await self.programmer(
                instruction=f"""Fix the following issues in the solution:
                Issues: {critique}
                Current solution: {current_solution}
                
                Requirements:
                - Address all identified flaws
                - Maintain function signature and type contracts
                - Return ONLY the function implementation with necessary imports""",
                context=current_solution
            )

        # Step 5: Ensemble synthesis - combine best elements
        final_solution = await self.ensemble(
            instruction=f"""Synthesize the best solution from these candidates:
            Candidate 1 (Reference style): {reference_approach}
            Candidate 2 (Hardened): {current_solution}
            Problem analysis: {problem_analysis}
            
            Selection criteria:
            1. Correctness (must pass all adversarial cases)
            2. Type safety and signature compliance
            3. Edge case robustness
            4. Code clarity and maintainability
            5. Match to reference solution approach when appropriate
            
            Return ONLY the final function implementation with necessary imports.
            Strip all explanations, comments, or extra text.""",
            contexts_list=[reference_approach, current_solution]
        )

        # Step 6: Final sanitization - ensure clean output format
        sanitized_solution = await self.summarize(
            instruction="""Extract ONLY the Python function implementation from this text.
            Requirements:
            - Must start with 'def function_name(...):'
            - Must include any necessary imports at top
            - Must contain ONLY code - no explanations, no comments, no markdown
            - Preserve exact whitespace and formatting of the code
            If multiple functions, extract only the one matching the problem's function signature.""",
            context=final_solution
        )

        return sanitized_solution