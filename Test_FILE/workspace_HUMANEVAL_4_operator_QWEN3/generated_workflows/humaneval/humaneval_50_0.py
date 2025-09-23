# Workflow ID: humaneval_50_0
# Benchmark: humaneval
# Data Indices: [92, 120]

# --- DO NOT IMPORT HERE ---
class Workflow:
    def __init__(self, config, problem) -> None:
        # --- DO NOT MODIFY THIS SECTION ---
        self.config = config
        self.problem_text = problem
        self.llm = create(config)
        
        self.generate = operator.Generate(self.llm, self.problem_text)
        self.revise = operator.Revise(self.llm, self.problem_text)
        self.summarize = operator.Summarize(self.llm, self.problem_text)
        self.ensemble = operator.Ensemble(self.llm, self.problem_text)

    async def run_workflow(self):
        """
        Universal workflow for code generation from specifications.
        Handles any problem in the domain by deeply analyzing examples,
        generating multiple solution candidates, and iteratively refining.
        """
        import asyncio
        import re

        # === PHASE 1: PARALLEL SPECIFICATION ANALYSIS ===
        # Generate three perspectives: constraints, logic, edge cases
        constraint_analysis = await self.generate(
            instruction="""Extract all explicit constraints from the specification:
            - Required input types and validations
            - Output format and type requirements
            - Preconditions and postconditions
            - Any mentioned limitations or guarantees
            Format as bullet points with clear labels.""",
            context=""
        )

        logic_analysis = await self.generate(
            instruction="""Infer the core algorithm from the examples:
            - What pattern or formula connects inputs to outputs?
            - Are there conditional branches or loops implied?
            - How do edge cases in examples affect the logic?
            - What operations (math, string, list) are involved?
            Describe the algorithm step by step.""",
            context=""
        )

        edge_case_analysis = await self.generate(
            instruction="""Identify all edge cases from examples and docstring:
            - Boundary values (0, empty, max/min)
            - Type variations (int vs float, string formats)
            - Error conditions or special returns
            - Any 'gotchas' implied by example outputs
            List each edge case with the example that reveals it.""",
            context=""
        )

        # Ensemble into unified spec
        synthesized_spec = await self.ensemble(
            instruction="""Synthesize the three analyses into one coherent specification:
            - Combine constraints, logic, and edge cases without redundancy
            - Prioritize requirements that appear in multiple analyses
            - Flag any contradictions or ambiguities
            - Structure as: 1) Input Requirements, 2) Core Logic, 3) Edge Cases, 4) Output Format
            This will guide all subsequent code generation.""",
            contexts_list=[constraint_analysis, logic_analysis, edge_case_analysis]
        )

        # === PHASE 2: DUAL SOLUTION GENERATION ===
        # Generate literal (minimal) and defensive (explicit) solutions
        literal_solution = await self.generate(
            instruction=f"""Generate the most minimal, literal implementation:
            - Use only what is explicitly required by this spec:
            {synthesized_spec}
            - No comments, no extra checks, no defensive programming
            - Match example outputs exactly
            - Use simplest possible constructs
            Return ONLY the function code, nothing else.""",
            context=synthesized_spec
        )

        defensive_solution = await self.generate(
            instruction=f"""Generate a defensive, explicit implementation:
            - Include type checks and edge case handling from spec:
            {synthesized_spec}
            - Add clear variable names and minimal comments for clarity
            - Ensure all example cases are handled explicitly
            - Still avoid over-engineering - no extra features
            Return ONLY the function code, nothing else.""",
            context=synthesized_spec
        )

        # === PHASE 3: VALIDATION-AWARE REVISION ===
        # Revise each against spec
        revised_literal = await self.revise(
            instruction=f"""Revise this code against the spec:
            SPEC: {synthesized_spec}
            CRITIQUE: Does it handle all edge cases? Correct return types? 
            Match examples exactly? Remove ANY logic not explicitly required.
            Return ONLY the corrected function code.""",
            context=literal_solution
        )

        revised_defensive = await self.revise(
            instruction=f"""Revise this code against the spec:
            SPEC: {synthesized_spec}
            CRITIQUE: Does it handle all edge cases? Correct return types?
            Is it minimal? Remove ANY checks or logic not mandated by spec.
            Return ONLY the corrected function code.""",
            context=defensive_solution
        )

        # === PHASE 4: SOLUTION SELECTION ===
        final_solution = await self.ensemble(
            instruction="""Select the best solution:
            - Must implement exactly what is specified, nothing more
            - Must handle all edge cases from examples
            - Prefer simpler, more minimal code unless complexity is required
            - Ensure function name matches ENTRY POINT exactly
            Return ONLY the selected function code, nothing else.""",
            contexts_list=[revised_literal, revised_defensive]
        )

        # === PHASE 5: ITERATIVE REFINEMENT (up to 2 cycles) ===
        current_solution = final_solution
        for i in range(2):
            critique = await self.generate(
                instruction=f"""Critique this code against the original specification:
                SPEC: {synthesized_spec}
                CODE: {current_solution}
                Identify ANY deviation: missing edge cases, wrong return types, 
                unnecessary logic, or mismatch with examples. Be specific.
                If perfect, respond ONLY with 'No issues found'.""",
                context=current_solution
            )
            
            if "no issues found" in critique.lower():
                break
                
            current_solution = await self.revise(
                instruction=f"""Fix all issues identified in critique:
                CRITIQUE: {critique}
                SPEC: {synthesized_spec}
                Return ONLY the corrected function code, nothing else.""",
                context=current_solution
            )

        # === PHASE 6: FINAL SANITIZATION ===
        sanitized_code = await self.revise(
            instruction="""Final cleanup:
            - Remove ALL comments, debug prints, or extra text
            - Ensure ONLY the function definition remains
            - Verify function name matches ENTRY POINT exactly
            - No imports, no extra lines, no explanations
            Return ONLY the clean function code.""",
            context=current_solution
        )

        return sanitized_code