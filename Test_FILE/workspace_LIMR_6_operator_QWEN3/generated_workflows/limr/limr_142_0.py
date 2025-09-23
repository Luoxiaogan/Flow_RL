# Workflow ID: limr_142_0
# Benchmark: limr
# Data Indices: [173, 201]

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

        # STEP 1: META-ANALYSIS — Classify problem type and extract mathematical essence
        problem_analysis = await self.generate(
            instruction="""
            Perform a deep structural analysis of this mathematical problem. Your task:

            1. Classify the primary mathematical domain (e.g., algebra, number theory, combinatorics, geometry, optimization, sequences).
            2. Identify key entities: variables, constraints, functions, domains, ranges, known values.
            3. Detect applicable theorems, identities, or strategies (e.g., Vieta’s formulas, AM-GM, modular arithmetic, Lagrange multipliers).
            4. Determine if the problem naturally decomposes into ordered subproblems.
            5. Predict the most promising 2-3 solution approaches.
            6. Flag any ambiguities or potential misinterpretations in the problem statement.

            Format your response as a structured report with clear section headers.
            """,
            context=""
        )

        # STEP 2: CONDITIONAL DECOMPOSITION — Only if problem has clear sequential structure
        decomposition = None
        if "decompos" in problem_analysis.lower() or "step" in problem_analysis.lower() or "subproblem" in problem_analysis.lower():
            try:
                decomposition = await self.decompose(
                    instruction="""
                    Break this problem into minimal, logically ordered subproblems. For each:
                    - State what needs to be solved
                    - List dependencies (which subproblems must be solved first)
                    - Estimate difficulty or risk of each step
                    Prioritize clarity and logical flow over granularity.
                    """,
                    context=problem_analysis
                )
            except Exception:
                decomposition = None  # Fallback if decomposition fails

        # STEP 3: PARALLEL STRATEGY EXPLORATION — Generate 3 distinct solution approaches
        strategy_instructions = [
            """
            Adopt an ALGEBRAIC/ANALYTIC lens. Focus on:
            - Symbolic manipulation
            - Equation solving
            - Function properties
            - Inequalities or optimization via calculus
            Derive the answer through formal mathematical reasoning. Show all steps.
            """,
            """
            Adopt a NUMBER THEORETIC/COMBINATORIAL lens. Focus on:
            - Integer properties, primes, divisibility
            - Counting, permutations, modular arithmetic
            - Diophantine constraints
            - Generating functions or recursive relations
            Derive the answer through discrete mathematical reasoning.
            """,
            """
            Adopt a COMPUTATIONAL/GEOMETRIC lens. Focus on:
            - Coordinate geometry, vectors, transformations
            - Numerical methods, search, or simulation
            - Visualization or spatial reasoning
            - Algorithmic construction
            If applicable, prepare for code-based verification.
            """
        ]

        # Generate 3 parallel solution attempts
        solution_attempts = await asyncio.gather(
            *[self.generate(instruction=instr, context=problem_analysis) for instr in strategy_instructions]
        )

        # STEP 4: SUMMARIZE EACH ATTEMPT for efficient ensembling
        summarized_attempts = await asyncio.gather(
            *[self.summarize(
                instruction="Extract the core reasoning path and final numerical answer. Ignore verbose steps. If no answer, state 'INCOMPLETE'.",
                context=attempt
            ) for attempt in solution_attempts]
        )

        # STEP 5: ENSEMBLE — Synthesize or select best answer
        ensemble_result = await self.ensemble(
            instruction="""
            You are given 3 solution attempts for a challenging math problem. Your task:

            1. Compare their reasoning quality, logical consistency, and adherence to constraints.
            2. Check for numerical agreement — do they converge on the same answer?
            3. If one is clearly superior (rigorous, complete, elegant), select it.
            4. If multiple are valid, synthesize a unified answer.
            5. If all are flawed, identify the most promising partial result and flag for revision.

            Output ONLY the final integer answer (000-999) if confident. Otherwise, output 'REVISION_NEEDED' and explain why.
            """,
            contexts_list=summarized_attempts
        )

        # STEP 6: VALIDATION & REVISION LOOP (max 2 iterations)
        final_answer = None
        for _ in range(2):
            if "REVISION_NEEDED" not in ensemble_result and re.search(r'\b\d{1,3}\b', ensemble_result):
                # Extract integer answer
                match = re.search(r'\b(\d{1,3})\b', ensemble_result)
                if match:
                    candidate = int(match.group(1))
                    if 0 <= candidate <= 999:
                        final_answer = f"{candidate:03d}"
                        break

            # If not confident, revise the most promising attempt
            revision_target = summarized_attempts[0]  # Default to first
            for i, sa in enumerate(summarized_attempts):
                if "INCOMPLETE" not in sa and "ERROR" not in sa.upper():
                    revision_target = solution_attempts[i]
                    break

            revised_attempt = await self.revise(
                instruction=f"""
                CRITICAL REVISION REQUEST:
                Previous attempts were inconclusive. Revise this solution with extreme rigor:

                - Verify every algebraic step
                - Check boundary conditions and constraints
                - Confirm domain/range compliance
                - Recompute critical values
                - Consider edge cases or alternative interpretations

                If possible, invoke computational verification for key steps.
                Output the final answer as a 3-digit integer (000-999) if certain.
                """,
                context=revision_target
            )

            # Attempt computational verification if numbers are present
            numbers = re.findall(r'\b\d+\b', revised_attempt)
            if len(numbers) > 0:
                try:
                    verification_code = await self.programmer(
                        instruction=f"""
                        Write Python code to verify the key numerical claim in this solution.
                        The problem involves: {problem_analysis[:200]}...
                        The proposed answer is: {revised_attempt[:300]}...
                        Compute the correct value directly if possible.
                        Output only the integer result.
                        """,
                        context=revised_attempt
                    )
                    # Extract number from code output
                    code_match = re.search(r'\b(\d{1,3})\b', verification_code)
                    if code_match:
                        candidate = int(code_match.group(1))
                        if 0 <= candidate <= 999:
                            final_answer = f"{candidate:03d}"
                            break
                except Exception:
                    pass  # Fallback to revised_attempt parsing

            # Re-summarize and re-ensemble
            revised_summary = await self.summarize(
                instruction="Extract final numerical answer. Output only the number or 'UNKNOWN'.",
                context=revised_attempt
            )
            ensemble_result = revised_summary
            if re.search(r'\b\d{1,3}\b', revised_summary):
                match = re.search(r'\b(\d{1,3})\b', revised_summary)
                candidate = int(match.group(1))
                if 0 <= candidate <= 999:
                    final_answer = f"{candidate:03d}"
                    break

        # STEP 7: FINAL OUTPUT — Ensure 3-digit format
        if final_answer is None:
            # Last resort: extract any 1-3 digit number from final ensemble
            fallback_match = re.search(r'\b(\d{1,3})\b', ensemble_result)
            if fallback_match:
                candidate = int(fallback_match.group(1))
                if 0 <= candidate <= 999:
                    final_answer = f"{candidate:03d}"
                else:
                    final_answer = "000"  # Default fallback
            else:
                final_answer = "000"

        return final_answer