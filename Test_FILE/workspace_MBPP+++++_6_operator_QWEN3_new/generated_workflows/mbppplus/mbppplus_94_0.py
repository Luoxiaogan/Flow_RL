# Workflow ID: mbppplus_94_0
# Benchmark: mbppplus
# Data Indices: [94, 295]

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

        # Step 1: Parallel generation of 3 distinct solution candidates
        candidate_instructions = [
            """You are an expert Python programmer. Generate a function that solves the problem exactly as specified.
            - Use the exact function name and parameters from the reference.
            - Handle edge cases: empty inputs, single elements, duplicates, type boundaries.
            - Return the correct data type (list/tuple/set) as implied by test cases.
            - Include necessary imports at the top.
            - Prioritize mathematical elegance and functional style.
            - Do not add comments or explanations — only code.
            - Ensure the code is complete and runnable as-is.""",
            
            """You are a pragmatic Python engineer. Generate a function that solves the problem reliably.
            - Use the exact function name and parameters.
            - Explicitly check for edge cases: empty inputs, None values, zero-length collections.
            - Use imperative style with clear, step-by-step logic.
            - Include defensive checks and type handling.
            - Return exactly what the test cases expect.
            - Include all imports.
            - Code must be self-contained and runnable.""",
            
            """You are a minimalist Python coder. Generate the most concise, readable solution possible.
            - Exact function signature required.
            - Leverage built-in functions and comprehensions.
            - Assume inputs are well-formed but still handle empty/single cases.
            - Prioritize clarity and brevity.
            - Match return type precisely.
            - No extra imports or comments.
            - Code must pass hidden test cases including edge conditions."""
        ]

        candidates = await asyncio.gather(
            *[self.generate(instruction=instr, context="") for instr in candidate_instructions]
        )

        # Step 2: Revise each candidate for edge cases and structural compliance
        edge_case_instruction = """Revise this code to ensure:
        - Handles empty inputs (e.g., empty tuple, empty list) without error.
        - Handles single-element inputs correctly.
        - Preserves expected return type (tuple/list/set) exactly.
        - Uses correct function name and parameter names.
        - Includes all necessary imports at the top.
        - No wrapper functions or classes — only the target function.
        - Returns appropriate values for boundary cases.
        - Code is robust against duplicates, negative numbers, and type edge cases.
        - Output must be runnable as standalone Python code."""

        revised_candidates = await asyncio.gather(
            *[self.revise(instruction=edge_case_instruction, context=cand) for cand in candidates]
        )

        # Step 3: Ensemble synthesis — select the most robust and clean solution
        ensemble_instruction = """You are a senior code reviewer. Select the BEST solution from the candidates below.
        Criteria in order of priority:
        1. Correctness: Must handle all edge cases (empty, single, boundary).
        2. Structural compliance: Exact function name, parameters, return type, imports.
        3. Readability: Clean, clear, and idiomatic Python.
        4. Efficiency: Avoid unnecessary complexity or operations.
        5. Test coverage: Implicitly satisfies diverse test cases.
        
        Do NOT combine solutions. Choose ONE candidate that best meets all criteria.
        Return ONLY the selected code — no explanations, no markdown, no extra text."""

        synthesized = await self.ensemble(
            instruction=ensemble_instruction,
            contexts_list=revised_candidates
        )

        # Step 4: Fallback refinement — if synthesis shows uncertainty, refine once
        if any(keyword in synthesized.lower() for keyword in ["error", "assume", "might", "could", "perhaps", "if"]):
            final_refine_instruction = """This code must be production-ready and handle all edge cases without assumptions.
            - Remove any conditional language or uncertainty.
            - Ensure it runs correctly for empty inputs, single elements, and boundary values.
            - Verify function signature and return type match exactly.
            - Make it robust and deterministic.
            - Return ONLY the final, corrected code."""
            
            synthesized = await self.revise(
                instruction=final_refine_instruction,
                context=synthesized
            )

        return synthesized