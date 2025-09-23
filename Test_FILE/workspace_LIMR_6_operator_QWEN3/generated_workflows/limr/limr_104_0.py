# Workflow ID: limr_104_0
# Benchmark: limr
# Data Indices: [278, 188]

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

        # STEP 1: INITIAL CLASSIFICATION & STRATEGIC ANALYSIS
        classification = await self.generate(
            instruction="""Perform deep problem classification and strategic reconnaissance. Specifically:
            1. Identify the primary mathematical domain (algebra, number theory, combinatorics, geometry, etc.)
            2. Extract all given variables, constraints, and boundary conditions.
            3. Determine the expected answer format (single integer? sum of possibilities? modular result?)
            4. Hypothesize 2-3 distinct solution strategies with brief rationale for each.
            5. Flag any potential pitfalls, domain restrictions, or non-obvious transformations.
            Structure your response clearly with labeled sections.""",
            context=""
        )

        # STEP 2: PARALLEL SOLUTION PATH EXPLORATION (Diamond Pattern)
        solution_attempts = await asyncio.gather(
            self.generate(
                instruction=f"""Solve the problem using ALGEBRAIC/ANALYTIC approach:
                - Leverage symbolic manipulation, equation solving, functional transformations
                - Show all intermediate steps with clear justification
                - Verify domain restrictions and edge cases
                - Box final answer as integer 000-999
                Context from classification: {classification}""",
                context=classification
            ),
            self.generate(
                instruction=f"""Solve the problem using COMBINATORIAL/ENUMERATIVE approach:
                - Consider counting principles, case analysis, recursive decomposition
                - If applicable, model as states or generate explicit cases
                - Avoid brute force unless space is small; prefer combinatorial identities
                - Box final answer as integer 000-999
                Context from classification: {classification}""",
                context=classification
            ),
            self.generate(
                instruction=f"""Solve the problem using NUMBER THEORETIC/STRUCTURAL approach:
                - Apply modular arithmetic, divisibility, prime factorization, or Diophantine techniques
                - Look for invariants, periodicity, or structural symmetries
                - Validate with small cases or counterexamples
                - Box final answer as integer 000-999
                Context from classification: {classification}""",
                context=classification
            )
        )

        # STEP 3: RIGOR REVISION OF EACH SOLUTION PATH
        revised_solutions = []
        for i, attempt in enumerate(solution_attempts):
            revised = await self.revise(
                instruction=f"""CRITICAL REVISION FOR MATHEMATICAL RIGOR:
                - Verify every algebraic step for correctness
                - Check divisibility conditions, domain validity, and edge cases
                - Ensure no division by zero or invalid operations
                - Cross-validate intermediate results if possible
                - If error found, correct it and re-derive
                - Preserve final boxed answer format
                Focus on logical completeness and precision.""",
                context=attempt
            )
            revised_solutions.append(revised)

        # STEP 4: ENSEMBLE SYNTHESIS & ANSWER EXTRACTION
        final_answer = await self.ensemble(
            instruction="""SYNTHESIZE AND SELECT FINAL ANSWER:
            1. Compare all revised solution paths.
            2. Identify consensus results or most rigorous derivation.
            3. If multiple valid answers exist (e.g., "sum of all possible"), aggregate them.
            4. Output ONLY the final integer answer between 000 and 999, with no explanation.
            5. If contradictions exist, select the solution with complete step-by-step verification.
            6. If no clear answer, output "UNKNOWN" (will trigger fallback).""",
            contexts_list=revised_solutions
        )

        # STEP 5: CONDITIONAL FALLBACK TO COMPUTATIONAL DECOMPOSITION
        if "UNKNOWN" in final_answer or not re.match(r'^\d{3}$', final_answer.strip()):
            # Decompose into computational subproblems
            subproblems = await self.decompose(
                instruction="""DECOMPOSE INTO COMPUTATIONAL SUBPROBLEMS:
                - Break problem into minimal, code-solvable units
                - Each subproblem must have clear inputs and expected outputs
                - Specify dependencies between subproblems
                - Focus on parts requiring enumeration, iteration, or exact calculation
                Return as structured list with 'id', 'description', 'dependencies'.""",
                context=classification
            )
            
            # Solve subproblems respecting dependencies
            subproblem_results = {}
            for sp in subproblems:
                # Wait for dependencies
                dep_results = "\n".join([f"{dep_id}: {subproblem_results[dep_id]}" 
                                       for dep_id in sp['dependencies'].split(',') 
                                       if dep_id.strip() and dep_id in subproblem_results])
                
                # Solve current subproblem
                code_result = await self.programmer(
                    instruction=f"""Solve this computational subproblem:
                    {sp['description']}
                    Use previous results if needed: {dep_results}
                    Output only the numerical result, no explanation.""",
                    context=dep_results
                )
                subproblem_results[sp['id']] = code_result.strip()

            # Synthesize computational results into final answer
            synthesis_context = "\n".join([f"{k}: {v}" for k,v in subproblem_results.items()])
            final_answer = await self.generate(
                instruction=f"""SYNTHESIZE COMPUTATIONAL RESULTS INTO FINAL ANSWER:
                Subproblem results: {synthesis_context}
                Combine these results according to original problem requirements.
                Output ONLY the final integer answer between 000 and 999.
                If sum of possibilities, sum them. If modular, apply mod.
                No explanation, just the number.""",
                context=synthesis_context
            )

        # STEP 6: FINAL VALIDATION & FORMATTING
        # Ensure output is clean 3-digit integer
        match = re.search(r'\b\d{1,3}\b', final_answer)
        if match:
            answer = int(match.group())
            return f"{answer:03d}"  # Zero-pad to 3 digits
        else:
            # Emergency fallback: maximal effort generate
            final_attempt = await self.generate(
                instruction="""EMERGENCY OVERRIDE - MAXIMAL EFFORT:
                You are a world-class mathematician. Solve this problem from first principles.
                Show every step with complete rigor. Consider all cases. Verify twice.
                Output format: ONLY the final integer answer between 000 and 999, boxed.
                Example: \\boxed{456}""",
                context=""
            )
            match = re.search(r'\b\d{1,3}\b', final_attempt)
            if match:
                answer = int(match.group())
                return f"{answer:03d}"
            else:
                return "000"  # Absolute fallback