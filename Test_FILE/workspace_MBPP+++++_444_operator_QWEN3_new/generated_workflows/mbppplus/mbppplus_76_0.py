# Workflow ID: mbppplus_76_0
# Benchmark: mbppplus
# Data Indices: [217, 150, 155]

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

        # PHASE 1: Problem Understanding & Constraint Extraction
        problem_analysis = await self.generate(
            instruction="""Perform deep structural analysis of this programming problem. Extract:
            1. Problem category (string manipulation, math, data structure, logic, regex, etc.)
            2. Input types and constraints (empty cases, edge values, data structures)
            3. Expected output type and format (int, str, bool, tuple, etc.)
            4. Key operations needed (iteration, recursion, regex, arithmetic, etc.)
            5. Mentioned or implied edge cases (empty input, single element, duplicates, boundaries)
            6. Required imports (if any modules like 're' are hinted)
            7. Function signature requirements (parameter names, return type)
            Format as a structured bullet-point summary.""",
            context=""
        )

        # PHASE 2: Parallel Hypothesis Generation (3 different solution approaches)
        hypothesis_instructions = [
            """You are a pragmatic programmer. Solve the problem with simplest possible approach.
            Focus on: direct iteration, basic conditionals, minimal abstractions.
            Explicitly handle: empty inputs, type consistency, boundary conditions.
            Return EXACT required data type. Include necessary imports at top.""",
            
            """You are an algorithm specialist. Solve with optimal data structures and patterns.
            Consider: recursion, divide-and-conquer, built-in methods, efficiency.
            Handle edge cases systematically. Preserve order if relevant.
            Match function signature exactly. Include imports if needed.""",
            
            """You are a defensive coder. Prioritize robustness over elegance.
            Add explicit checks for: None inputs, type mismatches, index bounds, empty collections.
            Use verbose variable names. Comment key logic. Return correct type always.
            Import modules if there's any chance they're needed."""
        ]

        hypotheses = await asyncio.gather(
            *[self.generate(instruction=inst, context=problem_analysis) for inst in hypothesis_instructions]
        )

        # PHASE 3: Ensemble Synthesis - Combine best elements from all hypotheses
        synthesized_solution = await self.ensemble(
            instruction=f"""Synthesize the best solution from these three attempts:
            - Preserve correct function signature and return type
            - Incorporate robustness features from defensive approach
            - Adopt efficiency from algorithmic approach
            - Keep simplicity where possible
            - Ensure ALL edge cases mentioned in analysis are handled
            - Verify imports are included if needed
            - Return ONLY the function implementation (no explanations)
            Problem analysis for reference: {problem_analysis}""",
            contexts_list=hypotheses
        )

        # PHASE 4: Validation & Hardening - Fix common pitfalls
        final_solution = await self.revise(
            instruction=f"""Critically review this code against ALL common pitfalls:
            1. Does it handle empty inputs? (empty string, empty list, etc.)
            2. Is return type EXACTLY as required? (tuple vs list vs set)
            3. Are all necessary imports included? (re, math, etc.)
            4. Does it preserve order when required?
            5. Are there off-by-one errors in loops or indices?
            6. Does it handle duplicates correctly?
            7. Are negative numbers or special values handled?
            8. Is the function signature preserved exactly?
            9. No outer wrappers or classes - ONLY function implementation
            Fix any issues found. Return ONLY the corrected code.""",
            context=synthesized_solution
        )

        return final_solution