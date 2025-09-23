# Workflow ID: mbppplus_69_0
# Benchmark: mbppplus
# Data Indices: [62, 265, 63]

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

        # Phase 1: Deep Structural Analysis
        problem_analysis = await self.generate(
            instruction="""Perform a comprehensive structural analysis of this programming problem. Extract and organize:
            1. Exact function signature and return type requirements
            2. Input parameter types and constraints
            3. Expected behavior from test cases (even if not shown, infer from domain)
            4. Edge cases that must be handled (empty inputs, boundaries, type edge cases)
            5. Algorithmic category (mathematical, string, list, logic, etc.)
            6. Potential failure modes and common pitfalls
            7. Required imports or language features
            Present as a structured, detailed breakdown with clear section headers.""",
            context=""
        )

        # Phase 2: Parallel Solution Generation (Diamond Pattern)
        solution_approaches = [
            """Generate a mathematically rigorous solution. Derive formulas algebraically. 
            Show step-by-step reasoning. Handle edge cases explicitly. 
            Optimize for correctness over performance. 
            Include comments explaining mathematical justification.
            Consider: modular arithmetic, series, combinatorics, number theory.""",
            
            """Generate an algorithmic/iterative solution. Use loops, conditionals, and basic operations. 
            Focus on clarity and robustness. Handle all edge cases explicitly. 
            Include loop invariants and termination conditions. 
            Optimize for readability and maintainability.""",
            
            """Generate a pragmatic/pythonic solution. Use built-in functions, comprehensions, and standard library. 
            Prioritize elegance and conciseness without sacrificing correctness. 
            Leverage Python's strengths (slicing, generators, itertools, etc.). 
            Include brief comments explaining clever optimizations."""
        ]

        candidate_solutions = await asyncio.gather(
            *[self.generate(
                instruction=f"""{approach}
                
                CRITICAL REQUIREMENTS:
                - Handle ALL edge cases: empty, single element, duplicates, negatives, zeros, boundaries
                - Match EXACT return type (list vs tuple vs set)
                - Include necessary imports
                - Function name and signature must match exactly
                - Return appropriate values for invalid inputs (often -1 or None)
                - Code must be self-contained and runnable
                
                Base your solution on this analysis:
                {problem_analysis}""",
                context=problem_analysis
            ) for approach in solution_approaches]
        )

        # Phase 3: Ensemble Synthesis with Cross-Validation
        synthesized_solution = await self.ensemble(
            instruction="""Synthesize the best elements from all candidate solutions into one optimal solution. 
            CRITICAL EVALUATION CRITERIA:
            1. Correctness: Which solution handles edge cases most comprehensively?
            2. Robustness: Which solution is least likely to fail on unseen test cases?
            3. Efficiency: Which solution has optimal time/space complexity?
            4. Clarity: Which solution is most readable and maintainable?
            5. Type Safety: Which solution best preserves required data types?
            
            Where solutions agree, that's high confidence. Where they disagree, analyze why and choose the most defensible approach.
            If any solution has a critical flaw, exclude it and explain why.
            Output ONLY the final function implementation with necessary imports - nothing else.
            Ensure function signature matches exactly and return type is correct.""",
            contexts_list=candidate_solutions
        )

        # Phase 4: Targeted Revision Loop (Adaptive Refinement)
        current_solution = synthesized_solution
        for iteration in range(3):  # Max 3 revision cycles
            revision_analysis = await self.generate(
                instruction=f"""Critically analyze this solution for common pitfalls:
                1. Does it handle empty inputs correctly?
                2. Does it preserve order when required?
                3. Does it return correct data type (list/tuple/set)?
                4. Does it handle duplicates properly?
                5. Are boundary conditions (min/max values) handled?
                6. Are negative numbers and zero handled appropriately?
                7. Is the function signature exactly as required?
                8. Are all necessary imports included?
                
                If NO issues found, respond with 'PASSED'.
                If issues found, describe them precisely and suggest fixes.
                
                Solution to analyze:
                {current_solution}""",
                context=current_solution
            )
            
            if "PASSED" in revision_analysis.upper():
                break
                
            current_solution = await self.revise(
                instruction=f"""Fix ALL issues identified in the analysis below. 
                Preserve the core logic but correct the flaws. 
                Maintain exact function signature and return type.
                Include necessary imports.
                Output ONLY the corrected function implementation.
                
                Issues to fix:
                {revision_analysis}""",
                context=current_solution
            )

        # Phase 5: Final Formatting and Type Enforcement
        final_implementation = await self.generate(
            instruction="""Output ONLY the function implementation with exact signature and necessary imports. 
            CRITICAL: 
            - NO extra text, explanations, or markdown
            - Function name and parameters must match exactly
            - Include ALL necessary imports at top
            - Return type must match problem requirements
            - Handle edge cases as previously analyzed
            - Code must be self-contained and runnable
            
            This is the final production code - it must be perfect.""",
            context=current_solution
        )

        return final_implementation