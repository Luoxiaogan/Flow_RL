# Workflow ID: mbppplus_127_0
# Benchmark: mbppplus
# Data Indices: [258, 282]

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

        # Step 1: Decompose the problem into core subtasks
        decomposition = await self.decompose(
            instruction="""Break down this programming problem into essential subtasks:
            1. Signature Analysis: Extract function name, parameters, and expected return type.
            2. Behavioral Inference: Deduce what the function must do from description and test cases.
            3. Edge Case Enumeration: Predict likely edge inputs (empty, singleton, duplicates, negatives, type mismatches).
            4. Strategy Selection: Suggest 2-3 viable implementation approaches (e.g., itertools, recursion, filtering, math ops).
            Return as structured list of subproblems with dependencies.""",
            context=""
        )

        # Step 2: Parallel strategy generation
        strategy_tasks = []
        for i, sub in enumerate(decomposition):
            if "Strategy Selection" in sub['description']:
                strategy_tasks.append(
                    self.generate(
                        instruction=f"""Propose a detailed implementation strategy for this problem:
                        - Use the function signature: {sub['description']}
                        - Consider edge cases: {', '.join([s['description'] for s in decomposition if 'Edge Case' in s['description']])}
                        - Prefer Pythonic, efficient, and readable code.
                        - Return code structure outline with key steps and libraries to use.""",
                        context=""
                    )
                )
        
        if not strategy_tasks:
            # Fallback: generate general strategy
            strategy_tasks = [
                self.generate(
                    instruction="""Propose a general implementation strategy:
                    - Analyze function signature and infer input/output types.
                    - Identify if problem is combinatorial, filtering, transformation, or mathematical.
                    - Suggest appropriate Python constructs (itertools, list comprehensions, recursion, etc.).
                    - Emphasize edge case handling and type consistency.""",
                    context=""
                )
            ]

        strategies = await asyncio.gather(*strategy_tasks)

        # Step 3: Synthesize best approach
        synthesized_strategy = await self.ensemble(
            instruction="""Synthesize the proposed strategies into one optimal approach:
            - Prioritize correctness, edge case coverage, and type safety.
            - Combine strengths: e.g., use itertools for core logic but add manual edge handling.
            - Ensure return type matches exactly (list vs tuple vs set).
            - Output a clear, step-by-step implementation plan with explicit edge case handling.""",
            contexts_list=strategies
        )

        # Step 4: Generate initial code
        code_attempt = await self.programmer(
            instruction=f"""Implement the function exactly as specified:
            - Follow this strategy: {synthesized_strategy}
            - Handle all edge cases: empty inputs, single elements, duplicates, negatives, type mismatches.
            - Return EXACTLY the expected type (list, tuple, set) as shown in test cases.
            - Do not add extra prints or comments unless necessary for correctness.
            - Validate input types if needed, but assume standard inputs unless specified otherwise.""",
            context="",
            max_retries=1
        )

        # Step 5: Iterative refinement loop (up to 3 rounds)
        current_code = code_attempt
        for iteration in range(3):
            # Validate and critique
            critique = await self.generate(
                instruction=f"""Critique this code rigorously:
                - Does it handle all edge cases (empty, singleton, duplicates, negatives)?
                - Does return type EXACTLY match expected (list/tuple/set)?
                - Is logic correct for sample inputs like [1,2,3] or [10,20]?
                - Are there any off-by-one errors, type mismatches, or logical flaws?
                - Suggest specific fixes if any issues found.
                Current code:
                {current_code}""",
                context=current_code
            )

            if "no issues" in critique.lower() or "correct" in critique.lower():
                break

            # Revise code based on critique
            current_code = await self.revise(
                instruction=f"""Fix all issues identified in critique:
                Critique: {critique}
                - Preserve function signature exactly.
                - Maintain type consistency.
                - Add explicit edge case handling if missing.
                - Do not change core logic unless necessary for correctness.""",
                context=current_code
            )

        # Step 6: Adversarial validation (final quality gate)
        adversarial_check = await self.generate(
            instruction=f"""You are a ruthless tester. Try to break this code:
            - What edge cases or inputs would cause failure?
            - Does it handle empty input? Single element? Duplicates? Negative numbers? Type mismatches?
            - Is return type exactly as expected?
            - If any vulnerability found, describe it precisely.
            Code to test:
            {current_code}""",
            context=current_code
        )

        if "vulnerability" in adversarial_check.lower() or "fails" in adversarial_check.lower():
            # Final emergency fix
            current_code = await self.revise(
                instruction=f"""Apply emergency fixes for vulnerabilities:
                Vulnerabilities: {adversarial_check}
                - Prioritize correctness over elegance.
                - Add explicit guards for edge cases.
                - Ensure type casting if needed.
                - Return must match expected type exactly.""",
                context=current_code
            )

        # Extract final code (assume it's in a markdown code block)
        # Simple extraction - in practice, use more robust parsing
        code_lines = current_code.split('\n')
        final_code = []
        in_code_block = False
        for line in code_lines:
            if line.strip().startswith('