# Workflow ID: humaneval_40_0
# Benchmark: humaneval
# Data Indices: [91, 147]

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

        # Phase 1: Specification Deconstruction
        spec_analysis = await self.generate(
            instruction="""Perform forensic analysis of the docstring examples to reverse-engineer the exact specification. Extract:
            1. Input type and structure (string, integer, list, etc.)
            2. Output type and format (int, float, bool, etc.) with precision requirements
            3. Delimiters, boundaries, or separators used in transformations
            4. Transformation rules (e.g., "starts with 'I'", "multiple of 3")
            5. Edge cases implied by examples (empty inputs, single elements, boundary conditions)
            6. Indexing conventions (0-based vs 1-based) if applicable
            7. Case sensitivity and whitespace handling rules
            Present findings as a structured bullet-point list with verbatim examples as evidence.""",
            context=""
        )

        # Phase 2: Parallel Strategy Exploration
        strategy_tasks = [
            self.generate(
                instruction=f"""Assuming this is a STRING/REGEX problem, outline a solution strategy.
                Use findings from specification analysis:
                {spec_analysis}
                
                Include:
                - Key regex patterns or string methods needed
                - Step-by-step transformation logic
                - How to handle edge cases identified
                - Pseudocode outline with critical operations
                Focus on text parsing, splitting, and pattern matching.""",
                context=spec_analysis
            ),
            self.generate(
                instruction=f"""Assuming this is a MATHEMATICAL/COMBINATORIAL problem, outline a solution strategy.
                Use findings from specification analysis:
                {spec_analysis}
                
                Include:
                - Formulas or sequences to generate
                - Mathematical properties to exploit (e.g., modular arithmetic)
                - Algorithmic approach (brute force, optimized, etc.)
                - Pseudocode with nested loops or mathematical operations
                Focus on calculations, sequences, and combinatorial logic.""",
                context=spec_analysis
            ),
            self.generate(
                instruction=f"""Assuming this is an ITERATIVE/LIST-PROCESSING problem, outline a solution strategy.
                Use findings from specification analysis:
                {spec_analysis}
                
                Include:
                - Data structures needed (lists, arrays, etc.)
                - Iteration patterns (sliding windows, nested loops, etc.)
                - Filtering or mapping operations
                - Pseudocode with explicit index handling
                Focus on list transformations and element-wise operations.""",
                context=spec_analysis
            )
        ]
        strategy_sketches = await asyncio.gather(*strategy_tasks)

        # Phase 3: Ensemble Synthesis with Constraint Injection
        best_strategy = await self.ensemble(
            instruction=f"""Select the SINGLE most appropriate strategy from the three options below.
            CRITICAL SELECTION CRITERIA:
            - Must perfectly match the specification analysis
            - Must handle all edge cases identified
            - Must use the most efficient approach for the problem type
            - Must align with examples' input/output patterns
            
            After selection, revise the chosen strategy by injecting these HARD CONSTRAINTS:
            1. Function name MUST exactly match the ENTRY POINT specified in the original problem
            2. Return type MUST match examples precisely (int vs float matters)
            3. Handle ALL edge cases from specification analysis
            4. No over-engineering - implement exactly what's specified
            5. Use 0-based indexing unless examples show 1-based
            6. Preserve case sensitivity and whitespace rules from examples
            
            Return only the revised strategy outline with injected constraints.""",
            contexts_list=strategy_sketches
        )

        # Phase 4: Code Generation with Self-Critique Loop
        code_draft = await self.generate(
            instruction=f"""Generate Python code implementing the strategy below.
            STRICT REQUIREMENTS:
            - Function name must exactly match ENTRY POINT from original problem
            - Return type must match examples (use int() or float() casting if needed)
            - Handle all edge cases from specification analysis
            - Include necessary imports (re, math, etc.) INSIDE function if needed
            - No extra functionality beyond specification
            - Use efficient algorithms but prioritize correctness over optimization
            
            Strategy to implement:
            {best_strategy}
            
            Return ONLY the function code with no additional text or explanations.""",
            context=best_strategy
        )

        # Iterative refinement with self-critique
        current_code = code_draft
        for iteration in range(3):  # Max 3 refinement cycles
            critique = await self.generate(
                instruction=f"""Critique this code against the specification:
                {spec_analysis}
                
                CHECKLIST:
                1. Does function name exactly match ENTRY POINT?
                2. Do return types match examples precisely?
                3. Are all edge cases from specification handled?
                4. Is there any over-engineering or extra functionality?
                5. Are delimiters/boundaries handled correctly?
                6. Is indexing consistent with examples?
                7. Are case sensitivity and whitespace rules respected?
                
                If any issues found, describe them specifically. If perfect, say "APPROVED".
                Return only the critique or "APPROVED".""",
                context=current_code
            )
            
            if "APPROVED" in critique.upper():
                break
                
            current_code = await self.revise(
                instruction=f"""Fix ALL issues identified in critique:
                {critique}
                
                Maintain all constraints from original strategy:
                {best_strategy}
                
                Return ONLY the revised function code with no additional text.""",
                context=current_code
            )

        return current_code