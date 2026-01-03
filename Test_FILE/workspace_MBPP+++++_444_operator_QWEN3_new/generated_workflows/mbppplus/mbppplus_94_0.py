# Workflow ID: mbppplus_94_0
# Benchmark: mbppplus
# Data Indices: [9, 289, 36]

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

        # PHASE 1: DECOMPOSE - Extract problem semantics, edge cases, and constraints
        decomposition = await self.generate(
            instruction="""Perform deep structural decomposition of this programming problem. Extract:
            1. INPUT SPEC: Exact types and structures of all parameters (e.g., 'list of integers', 'two arrays of same type')
            2. OUTPUT SPEC: Required return type and structure (e.g., 'list', 'integer index', 'boolean')
            3. OPERATION CATEGORY: Classify the core operation (e.g., 'index-based removal', 'set difference', 'equality check')
            4. INDEXING CONVENTION: Determine if indices are 0-based or 1-based from examples
            5. EDGE CASES: Infer at least 3 unshown edge cases (e.g., empty inputs, boundary indices, type mismatches)
            6. SIGNATURE CONSTRAINTS: Note any strict requirements (e.g., 'must return list not tuple', 'no imports allowed')
            Format as a structured JSON-like block with clear section headers.""",
            context=""
        )

        # PHASE 2: GENERATE CANDIDATES - Parallel generation of diverse implementation strategies
        candidate_instructions = [
            """Generate a MINIMALIST solution using the most direct Python idiom (e.g., slicing, built-ins). 
            Prioritize brevity and elegance. Use the problem decomposition to ensure type and edge case alignment.
            Example: For list removal, use slicing; for comparison, use direct equality.""",
            
            """Generate an EXPLICIT ITERATION solution using loops and index tracking. 
            Make all assumptions visible (e.g., index starting point, boundary checks). 
            Include inline comments explaining edge case handling based on the decomposition.""",
            
            """Generate a FUNCTIONAL STYLE solution using comprehensions, enumerate, or itertools if appropriate.
            Focus on immutability and expression-based logic. Ensure output type matches specification exactly."""
        ]

        candidate_tasks = [
            self.generate(instruction=f"{instr}\n\nUse this problem decomposition for context:\n{decomposition}", context="")
            for instr in candidate_instructions
        ]
        
        candidates = await asyncio.gather(*candidate_tasks)

        # PHASE 3: VALIDATE & SYNTHESIZE - Cross-examine candidates against edge cases and constraints
        validated_candidates = []
        for i, candidate in enumerate(candidates):
            validated = await self.revise(
                instruction=f"""Critically validate this candidate solution against the problem decomposition:
                - Does it handle ALL inferred edge cases from the decomposition?
                - Does it match the required input/output types exactly?
                - Is the indexing convention (0-based/1-based) correctly implemented?
                - Are there any off-by-one errors or boundary violations?
                - Does the function signature match exactly (parameter names, return type)?
                If any issues are found, revise the code to fix them. Preserve the original strategy (minimalist/explicit/functional) while hardening it.
                Problem Decomposition for reference:
                {decomposition}""",
                context=candidate
            )
            validated_candidates.append(validated)

        # PHASE 4: ENSEMBLE - Synthesize the best solution from validated candidates
        final_solution = await self.ensemble(
            instruction="""Select and synthesize the optimal solution from the candidates below. Criteria:
            1. CORRECTNESS: Must handle all edge cases and match type/signature requirements
            2. ROBUSTNESS: Most defensive against invalid inputs (without explicit error handling unless specified)
            3. SIMPLICITY: Prefer minimal, readable code that matches the problem's apparent complexity
            4. CONVENTION: Follows Python idioms unless problem implies otherwise
            If candidates are equally valid, prefer the minimalist approach. Output ONLY the final function implementation with imports if needed.
            Do NOT include explanations, markdown, or extra text — only the raw code block as specified in the problem requirements.""",
            contexts_list=validated_candidates
        )

        # PHASE 5: SELF-CORRECTION LOOP (max 2 iterations) - Ensure strict signature/type compliance
        for _ in range(2):
            signature_check = await self.generate(
                instruction=f"""Verify this solution against the original problem's function signature and output requirements:
                - Does the function name match exactly?
                - Are parameter names identical?
                - Is the return type correct (list vs tuple vs scalar)?
                - Are there any unnecessary imports or extra code?
                If ANY mismatch is found, output a concise correction instruction. Otherwise, output 'VALID'.
                Solution to check:
                {final_solution}""",
                context=""
            )
            
            if "VALID" in signature_check.upper():
                break
                
            final_solution = await self.revise(
                instruction=f"""Apply this correction to achieve strict compliance with the problem's signature and type requirements:
                {signature_check}
                Output ONLY the corrected function implementation — no explanations or markdown.""",
                context=final_solution
            )

        return final_solution