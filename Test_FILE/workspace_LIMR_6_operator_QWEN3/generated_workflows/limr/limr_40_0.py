# Workflow ID: limr_40_0
# Benchmark: limr
# Data Indices: [166, 329]

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

        # PHASE 1: STRUCTURAL DECOMPOSITION & ENTITY EXTRACTION
        decomposition_instruction = """
        Systematically deconstruct the problem into its mathematical primitives. Identify:
        1. All given quantities, variables, and constraints
        2. The explicit question being asked (final output format: integer 000-999)
        3. Hidden symmetries, invariants, or applicable theorems
        4. Potential solution domains (algebraic, geometric, combinatorial, etc.)
        5. Dependencies between subproblems
        Output as a numbered list of atomic subproblems with prerequisite relationships.
        """
        decomposition = await self.decompose(
            instruction=decomposition_instruction,
            context=""
        )
        
        # Summarize decomposition for downstream use
        decomposition_summary = await self.summarize(
            instruction="Condense the decomposition into a bullet-point list of key subproblems and their dependencies. Remove verbose explanations.",
            context=str(decomposition)
        )

        # PHASE 2: PARALLEL SOLUTION HYPOTHESIS GENERATION
        # Generate 3 distinct solution approaches using different mathematical lenses
        approach_instructions = [
            """
            Solve using SYNTHETIC/GEOMETRIC reasoning:
            - Leverage diagrams, angle chasing, similarity, congruence
            - Apply theorems (Pythagorean, Angle Bisector, etc.) without coordinates
            - Prioritize elegance and minimal computation
            """,
            """
            Solve using COORDINATE/ALGEBRAIC reasoning:
            - Assign coordinates to key points
            - Derive equations for lines, curves, or constraints
            - Solve system of equations algebraically
            - Emphasize computational rigor over geometric insight
            """,
            """
            Solve using VECTOR/TRANSFORMATIONAL reasoning:
            - Represent points as vectors
            - Use dot products, cross products, or matrix transformations
            - Exploit linear algebra or affine transformations
            - Focus on structural relationships over numerical values
            """
        ]

        # Launch parallel solution attempts
        solution_attempts = await asyncio.gather(
            *[self.generate(instruction=instr, context=decomposition_summary) 
              for instr in approach_instructions]
        )

        # PHASE 3: CRITIQUE & REFINEMENT LOOP
        refined_solutions = []
        for i, attempt in enumerate(solution_attempts):
            # Critique each attempt
            critique = await self.generate(
                instruction=f"""
                Critically evaluate Solution Attempt {i+1}:
                1. Verify all mathematical steps for logical consistency
                2. Check boundary conditions and edge cases
                3. Confirm final answer is an integer 000-999
                4. Identify any unjustified assumptions or leaps
                5. Suggest specific improvements or corrections
                """,
                context=attempt
            )
            
            # Revise based on critique
            refined = await self.revise(
                instruction=f"""
                Incorporate the critique to produce a flawless solution:
                - Fix all identified errors
                - Add missing justifications
                - Ensure computational precision
                - Explicitly state how the answer satisfies 000-999 constraint
                """,
                context=f"Original Attempt:\n{attempt}\n\nCritique:\n{critique}"
            )
            refined_solutions.append(refined)

        # PHASE 4: ENSEMBLE SYNTHESIS & ADVERSARIAL VALIDATION
        # Synthesize best solution from refined attempts
        synthesized_solution = await self.ensemble(
            instruction="""
            Select or synthesize the optimal solution considering:
            1. Mathematical rigor (no gaps in logic)
            2. Computational efficiency (minimal complex calculations)
            3. Elegance (fewest ad hoc assumptions)
            4. Robustness (handles edge cases)
            If solutions conflict, prioritize the one with explicit verification steps.
            Output ONLY the final answer as an integer between 000 and 999.
            """,
            contexts_list=refined_solutions
        )

        # Adversarial validation: try to break the solution
        adversarial_check = await self.generate(
            instruction=f"""
            Play devil's advocate: Assume the following solution is WRONG.
            Solution: {synthesized_solution}
            1. What is the MOST LIKELY error? (misapplied theorem, calculation mistake, etc.)
            2. What alternative interpretation could invalidate this answer?
            3. Propose a stress test (e.g., extreme values, degenerate cases)
            If no credible flaw exists, output "VERIFIED".
            """,
            context=decomposition_summary
        )

        # Final revision if adversarial check finds issues
        if "VERIFIED" not in adversarial_check.upper():
            final_answer = await self.revise(
                instruction=f"""
                Address the adversarial critique:
                Critique: {adversarial_check}
                1. Re-solve the problem accounting for the identified vulnerability
                2. Include explicit verification against the critique
                3. Output ONLY the final integer answer (000-999)
                """,
                context=synthesized_solution
            )
        else:
            final_answer = synthesized_solution

        # PHASE 5: CANONICALIZATION & OUTPUT
        # Ensure output is clean integer
        canonicalization = await self.programmer(
            instruction="""
            Extract the final integer answer from the text below. The answer must be:
            - An integer between 0 and 999
            - Zero-padded to 3 digits if necessary (e.g., 5 → 005)
            - No units, explanations, or symbols
            If multiple numbers exist, select the one that matches problem constraints.
            """,
            context=final_answer
        )

        # Fallback: if programmer fails, extract via regex
        match = re.search(r'\b([0-9]{1,3})\b', canonicalization)
        if match:
            answer = int(match.group(1))
            return f"{answer:03d}"
        else:
            # Last resort: return first 3-digit number from synthesized solution
            fallback_match = re.search(r'\b([0-9]{1,3})\b', synthesized_solution)
            if fallback_match:
                answer = int(fallback_match.group(1))
                return f"{answer:03d}"
            else:
                return "000"  # Default fallback