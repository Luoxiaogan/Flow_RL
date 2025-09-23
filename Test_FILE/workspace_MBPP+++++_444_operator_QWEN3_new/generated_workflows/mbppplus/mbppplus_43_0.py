# Workflow ID: mbppplus_43_0
# Benchmark: mbppplus
# Data Indices: [247, 267, 4]

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

    async def run_workflow(self):
        import asyncio
        import re

        # Stage 1: Problem Classification & Requirement Extraction
        classification = await self.generate(
            instruction="""Perform deep problem analysis. Classify the problem type and extract all implicit and explicit requirements.
            1. Identify input types (int, str, list, etc.) and output type.
            2. Determine if it's mathematical, string-based, logical, or data structure manipulation.
            3. List all edge cases that must be handled (empty inputs, negatives, single elements, duplicates, etc.).
            4. Note any constraints on time/space complexity or specific algorithms required.
            5. Extract the exact function signature and return type expectations.
            6. Identify potential failure points in naive implementations.
            Present as a structured markdown report with clear sections.""",
            context=""
        )

        # Stage 2: Parallel Strategy Generation
        strategy_tasks = [
            self.generate(
                instruction=f"""Generate a solution using direct formulaic/algorithmic approach.
                Classification context: {classification}
                Requirements:
                - Match exact function signature
                - Handle all edge cases identified
                - Prioritize correctness over cleverness
                - Include type-consistent returns
                - Add inline comments explaining key logic
                Return ONLY the function implementation with imports if needed.""",
                context=""
            ),
            self.generate(
                instruction=f"""Generate a solution using step-by-step procedural approach with explicit edge case handling.
                Classification context: {classification}
                Requirements:
                - Use defensive programming with explicit conditionals
                - Validate inputs where appropriate
                - Handle edge cases with dedicated branches
                - Include verbose comments for maintainability
                - Match exact return type and signature
                Return ONLY the function implementation with imports if needed.""",
                context=""
            ),
            self.generate(
                instruction=f"""Generate a solution using built-in Python methods and idiomatic patterns.
                Classification context: {classification}
                Requirements:
                - Leverage Python standard library optimally
                - Use slicing, comprehensions, or built-ins where appropriate
                - Ensure robustness against edge cases
                - Maintain readability and Pythonic style
                - Match exact function signature and return type
                Return ONLY the function implementation with imports if needed.""",
                context=""
            )
        ]
        
        strategy_solutions = await asyncio.gather(*strategy_tasks)

        # Stage 3: Parallel Validation & Critique
        validation_tasks = []
        for i, solution in enumerate(strategy_solutions):
            validation_tasks.append(
                self.revise(
                    instruction=f"""Critically review this solution as a senior code reviewer.
                    1. Verify it matches the exact function signature and return type.
                    2. Check handling of all edge cases identified in classification: {classification}
                    3. Identify any logical flaws, off-by-one errors, or type mismatches.
                    4. Assess efficiency and potential bottlenecks.
                    5. Note any missing input validation or boundary condition handling.
                    6. Suggest specific improvements without rewriting the entire solution.
                    Be brutally honest. If the solution is fundamentally flawed, say so explicitly.""",
                    context=solution
                )
            )
        
        solution_validations = await asyncio.gather(*validation_tasks)

        # Stage 4: Summarize Critiques for Ensemble
        summarized_validations = []
        for i, validation in enumerate(solution_validations):
            summary = await self.summarize(
                instruction="""Extract key findings from this code review:
                1. List specific bugs or flaws found
                2. Note edge cases handled well or poorly
                3. Highlight efficiency concerns
                4. Extract suggested improvements
                5. Give overall confidence score (0-100%)
                Format as bullet points with clear severity indicators.""",
                context=validation
            )
            summarized_validations.append(f"Solution {i+1} Review:\n{summary}\nOriginal Solution:\n{strategy_solutions[i]}")

        # Stage 5: Ensemble Synthesis
        final_solution = await self.ensemble(
            instruction="""You are the lead architect synthesizing the final solution. Your task:
            1. Analyze all candidate solutions and their validation summaries.
            2. Extract the strongest components from each (correct logic, robust edge handling, clean style).
            3. Resolve contradictions by prioritizing: correctness > edge-case robustness > efficiency > elegance.
            4. Ensure exact function signature and return type compliance.
            5. Incorporate all critical fixes from validation feedback.
            6. Optimize only where it doesn't compromise correctness or clarity.
            7. Return ONLY the final function implementation with necessary imports.
            Do NOT include any explanations, comments, or markdown - just the raw code as specified in requirements.""",
            contexts_list=summarized_validations
        )

        # Stage 6: Test Simulation & Final Polish
        test_simulation = await self.generate(
            instruction=f"""Simulate 5 hidden edge test cases this solution must handle. Verify the solution handles them correctly.
            If any failure is detected, return 'REVISION_NEEDED' followed by the specific issue.
            If all pass, return 'VALIDATED'.
            Edge cases to consider based on classification: {classification}""",
            context=final_solution
        )

        if "REVISION_NEEDED" in test_simulation:
            final_solution = await self.revise(
                instruction=f"""Fix the specific issue identified in test simulation: {test_simulation}
                Preserve all other correct functionality.
                Maintain exact function signature and return type.
                Return ONLY the corrected function implementation.""",
                context=final_solution
            )

        return final_solution