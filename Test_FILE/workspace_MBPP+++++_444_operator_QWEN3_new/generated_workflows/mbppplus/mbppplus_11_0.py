# Workflow ID: mbppplus_11_0
# Benchmark: mbppplus
# Data Indices: [364, 200, 325]

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

        # PHASE 1: PROBLEM DISCOVERY & CLASSIFICATION
        discovery = await self.generate(
            instruction="""Perform deep problem analysis:
            1. Classify problem type: string manipulation, mathematical recursion, set/list operations, logical validation, or other.
            2. Extract all explicit and implicit constraints.
            3. Infer expected input/output data types and structures.
            4. Hypothesize edge cases: empty inputs, single elements, duplicates, negatives, boundaries, type mismatches.
            5. Identify required algorithmic patterns: iteration, recursion, regex, memoization, etc.
            6. Note any format requirements: preserve order? return specific type? handle Unicode?
            Structure response with clear section headers.""",
            context=""
        )

        # PHASE 2: CONTEXT DISTILLATION (prevent context bloat)
        spec_sheet = await self.summarize(
            instruction="""Condense analysis into critical constraints checklist:
            - Bullet point format only
            - Include ONLY: problem type, key constraints, edge cases, output requirements
            - Omit examples, explanations, and redundant details
            - This will be used for solution validation""",
            context=discovery
        )

        # PHASE 3: PARALLEL STRATEGY GENERATION
        # Dynamically craft strategy instructions based on discovery
        strategy_instructions = [
            f"""Generate Python solution using APPROACH 1:
            Problem context: {discovery[:500]}...
            Constraints: {spec_sheet}
            Focus on: correctness, edge case handling, clean code.
            Include necessary imports inside function if needed.
            Return ONLY the function implementation with exact signature.""",
            
            f"""Generate Python solution using APPROACH 2 (alternative method):
            Problem context: {discovery[:500]}...
            Constraints: {spec_sheet}
            Use different algorithmic strategy than Approach 1 (e.g., if 1 uses recursion, use iteration; if 1 uses regex, use manual parsing).
            Prioritize efficiency and readability.
            Return ONLY the function implementation with exact signature."""
        ]

        # Generate multiple solution candidates in parallel
        solution_candidates = await asyncio.gather(
            self.generate(instruction=strategy_instructions[0], context=""),
            self.generate(instruction=strategy_instructions[1], context="")
        )

        # PHASE 4: ENSEMBLE SYNTHESIS
        synthesized_solution = await self.ensemble(
            instruction=f"""Synthesize best solution from candidates:
            Evaluation criteria:
            1. Correctness: Must handle all edge cases from spec: {spec_sheet}
            2. Robustness: Defensive programming, type safety, error prevention
            3. Efficiency: Avoid unnecessary complexity
            4. Readability: Clean, Pythonic code with good variable names
            5. Completeness: Exact function signature, necessary imports
            
            If one solution is superior, select it. If they complement each other, merge strengths.
            Return ONLY the final Python function implementation - no explanations or markdown.""",
            contexts_list=solution_candidates
        )

        # PHASE 5: ITERATIVE REFINEMENT (up to 2 rounds)
        current_solution = synthesized_solution
        for _ in range(2):
            critique = await self.generate(
                instruction=f"""Critique this solution mercilessly:
                Problem constraints: {spec_sheet}
                Check for:
                - Edge case failures (empty, single, boundary, invalid inputs)
                - Type mismatches (returning list vs tuple, etc.)
                - Logic errors or off-by-one mistakes
                - Efficiency bottlenecks
                - Violations of Python best practices
                If no issues found, respond exactly: "NO ISSUES FOUND"
                Otherwise, list specific fixes needed.""",
                context=current_solution
            )
            
            if "NO ISSUES FOUND" in critique.upper():
                break
                
            current_solution = await self.revise(
                instruction=f"""Fix all issues identified in critique:
                Critique: {critique}
                Constraints: {spec_sheet}
                Preserve function signature and core logic.
                Return ONLY the corrected Python function implementation.""",
                context=current_solution
            )

        # PHASE 6: FINAL CODE EXTRACTION & SANITIZATION
        final_code = await self.revise(
            instruction="""Extract ONLY the Python function implementation:
            - Remove all commentary, markdown, or explanations
            - Ensure exact function signature as in problem
            - Include necessary imports inside the function if used
            - Return raw code string with no wrapping or formatting""",
            context=current_solution
        )

        return final_code