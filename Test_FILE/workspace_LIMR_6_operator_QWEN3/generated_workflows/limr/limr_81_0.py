# Workflow ID: limr_81_0
# Benchmark: limr
# Data Indices: [93, 2]

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

        # PHASE 1: STRATEGIC DECOMPOSITION
        decomposition = await self.decompose(
            instruction="""Break this mathematical problem into atomic, solvable subproblems. For each:
            - Identify required mathematical domain (algebra, geometry, number theory, etc.)
            - List explicit constraints and given values
            - Note implicit assumptions (e.g., 'quadratic' implies degree 2)
            - Specify dependencies between subproblems
            Output as structured subproblem list with IDs and dependencies.""",
            context=""
        )

        # PHASE 2: PARALLEL SOLUTION ATTEMPTS (DIAMOND FORK)
        # Generate 3 distinct solution strategies
        strategy_instructions = [
            """Solve using ALGEBRAIC manipulation:
            - Express unknowns as variables
            - Derive equations from constraints
            - Solve system symbolically
            - Verify against all given conditions
            Show all steps. Assume nothing beyond problem statement.""",
            
            """Solve using GEOMETRIC/GRAPHICAL intuition:
            - Interpret functions/relations visually
            - Use asymptotes, intercepts, symmetries
            - Translate graphical features to algebraic constraints
            - Cross-validate with numerical points
            Describe reasoning spatially then convert to equations.""",
            
            """Solve using COMPUTATIONAL verification:
            - Identify minimal symbolic form
            - Generate code to solve equations/verify constraints
            - Test edge cases and given points
            - Output must be executable Python with assertions
            Prioritize correctness over elegance."""
        ]

        solution_attempts = await asyncio.gather(
            *[self.generate(instruction=instr, context="") for instr in strategy_instructions]
        )

        # PHASE 3: RIGOROUS REVISION & VALIDATION
        revised_attempts = []
        for i, attempt in enumerate(solution_attempts):
            # Revise for logical gaps and precision
            revised = await self.revise(
                instruction=f"""CRITICALLY REVISE this solution:
                - Check every algebraic step for errors
                - Verify all constraints are satisfied (substitute back!)
                - Ensure answer format is integer 000-999
                - If symbolic, derive final numeric answer
                - Flag any unjustified assumptions
                Strategy was: {strategy_instructions[i][:50]}...
                """,
                context=attempt
            )
            revised_attempts.append(revised)

        # PHASE 4: ENSEMBLE SYNTHESIS & CONFLICT DETECTION
        synthesis = await self.ensemble(
            instruction="""SYNTHESIZE solutions:
            - Extract final numeric answer from each attempt
            - If ≥2 agree, output consensus answer
            - If all differ, identify root cause of disagreement
            - If one is computational (code-based), prioritize it if verified
            - Format final answer as: "ANSWER: XXX" where XXX is 000-999""",
            contexts_list=revised_attempts
        )

        # PHASE 5: SPIRAL REFINEMENT (if conflict detected)
        if "disagree" in synthesis.lower() or "conflict" in synthesis.lower():
            for spiral in range(2):  # Max 2 refinement loops
                # Diagnose disagreement
                diagnosis = await self.generate(
                    instruction="""ANALYZE why solutions disagree:
                    - Compare key assumptions in each approach
                    - Identify which constraints were misapplied
                    - Suggest corrective transformation (e.g., 'use modular arithmetic', 'factor differently')
                    Output specific revision directives.""",
                    context=synthesis + "

" + "

".join(revised_attempts)
                )
                
                # Generate targeted revisions
                refined_solutions = await asyncio.gather(
                    *[self.revise(
                        instruction=f"""RE-SOLVE with correction: {diagnosis[:200]}...
                        - Address specific flaw identified
                        - Re-verify ALL constraints
                        - Output only final answer in format 'ANSWER: XXX'""",
                        context=attempt
                    ) for attempt in revised_attempts]
                )
                
                # Re-synthesize
                synthesis = await self.ensemble(
                    instruction="""FINAL SYNTHESIS:
                    - Extract numeric answers
                    - Choose most consistent OR code-verified answer
                    - If still conflicted, select answer from computational approach
                    - MUST output "ANSWER: XXX" format""",
                    contexts_list=refined_solutions
                )
                
                if not ("disagree" in synthesis.lower() or "conflict" in synthesis.lower()):
                    break

        # PHASE 6: PROGRAMMATIC VERIFICATION (if answer extractable)
        final_answer = synthesis
        try:
            # Extract answer for verification
            match = re.search(r"ANSWER:\s*(\d{3})", synthesis)
            if match:
                candidate_answer = match.group(1)
                
                # Generate verification code if problem is computational
                verification = await self.programmer(
                    instruction=f"""VERIFY answer {candidate_answer}:
                    - Recreate problem constraints in code
                    - Test if answer satisfies ALL conditions
                    - Output 'VERIFIED' or 'FAILED' with reason
                    - Use symbolic math if needed (sympy)""",
                    context=synthesis,
                    max_retries=2
                )
                
                if "VERIFIED" in verification:
                    final_answer = f"ANSWER: {candidate_answer}"
                else:
                    # Fall back to ensemble result if verification fails
                    pass
        except Exception:
            # Keep synthesis if extraction fails
            pass

        return final_answer