# Workflow ID: limr_136_0
# Benchmark: limr
# Data Indices: [302, 217]

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

        # === PHASE 1: META-CLASSIFICATION & STRATEGIC DECOMPOSITION ===
        classification = await self.generate(
            instruction="""Perform deep problem classification and strategic decomposition:
            1. Identify the primary mathematical domain (algebra, number theory, combinatorics, geometry, etc.)
            2. List all explicit and implicit constraints (e.g., integer answers, prime conditions, common roots)
            3. Recognize key patterns or symmetries (e.g., coefficient reversals, recursive structures, modular constraints)
            4. Propose 2-3 distinct high-level solution strategies with brief rationale for each
            5. Anticipate potential pitfalls or computationally expensive dead ends
            6. Estimate whether solution set is empty, finite, or infinite; if finite, rough cardinality
            Format as structured markdown with clear section headers.""",
            context=""
        )

        # === PHASE 2: HIERARCHICAL DECOMPOSITION INTO STRATEGIC SUBPROBLEMS ===
        decomposition = await self.decompose(
            instruction="""Decompose into strategic subproblems based on classification:
            - Each subproblem should represent a distinct solution approach or critical insight
            - Include dependencies only if one approach logically requires another
            - Focus on mathematical leverage points (symmetries, substitutions, known theorems)
            - At least one subproblem should involve computational verification
            Example: 
            id: "symmetry_approach"
            description: "Exploit coefficient symmetry by assuming reciprocal roots"
            dependencies: "" """,
            context=classification
        )

        # === PHASE 3: PARALLEL STRATEGY EXECUTION ===
        async def execute_strategy(subproblem):
            try:
                # Generate detailed mathematical approach
                approach = await self.generate(
                    instruction=f"""Develop complete mathematical solution for: {subproblem['description']}
                    - Start from first principles
                    - Show all algebraic/logical steps
                    - Highlight key insights or non-obvious transformations
                    - If applicable, derive general formula before specializing
                    - End with clear candidate answer(s) in boxed format""",
                    context=classification
                )
                
                # Extract potential computational tasks
                computation_needed = await self.generate(
                    instruction="""Identify any precise computations needed (roots, sums, primes, etc.).
                    If none, return "NONE". If yes, specify exact computation in Python-ready form.
                    Examples: 
                    - "Solve 1988*x^2 + b*x + 8891 = 0 for x in terms of b"
                    - "Find all primes p such that n^2 - 35n + 306 = p for integer n in [1,100]"
                    - "Compute gcd of coefficients 1988 and 8891\"""",
                    context=approach
                )
                
                computation_result = ""
                if "NONE" not in computation_needed.upper():
                    computation_result = await self.programmer(
                        instruction=f"""Execute this precise computation: {computation_needed}
                        - Use exact arithmetic (no floats)
                        - Return all solutions in specified range
                        - Format as comma-separated values or list""",
                        context=approach,
                        max_retries=3
                    )
                
                # Integrate computation and refine
                integrated = await self.revise(
                    instruction=f"""Integrate computational results and refine solution:
                    Computation: {computation_result}
                    - Verify consistency between symbolic and numeric results
                    - Check all constraints from original problem
                    - Ensure final answer is integer in [000,999] format
                    - If multiple answers, list all separated by commas
                    - Box final answer as ###ANSWER: [value]###""",
                    context=approach
                )
                
                # Independent verification
                verification = await self.generate(
                    instruction="""Critically verify this solution:
                    - Substitute answer back into original problem statement
                    - Check for logical gaps or unverified assumptions
                    - Confirm no cases missed (especially edge cases)
                    - Rate confidence: HIGH/MEDIUM/LOW with justification""",
                    context=integrated
                )
                
                return f"STRATEGY: {subproblem['id']}\n\nSOLUTION:\n{integrated}\n\nVERIFICATION:\n{verification}"
                
            except Exception as e:
                return f"STRATEGY: {subproblem['id']}\n\nFAILED: {str(e)}\n\nVERIFICATION: LOW confidence due to error"

        # Execute all strategies in parallel
        strategy_results = await asyncio.gather(
            *[execute_strategy(sp) for sp in decomposition]
        )

        # === PHASE 4: ENSEMBLE SYNTHESIS WITH CONFIDENCE-BASED SELECTION ===
        final_answer = await self.ensemble(
            instruction="""Synthesize final answer from all strategy results:
            1. Prioritize solutions with HIGH confidence verification
            2. If multiple HIGH confidence answers, check for consistency
            3. If inconsistent, identify which approach is most mathematically rigorous
            4. If all LOW/MEDIUM, select the most complete and attempt refinement
            5. Final output MUST be integers between 000-999, comma-separated if multiple
            6. Format as: ###FINAL_ANSWER: [values]### (e.g., ###FINAL_ANSWER: 123,456###)
            7. If no valid answer found, return ###FINAL_ANSWER: 000###""",
            contexts_list=strategy_results
        )

        # === PHASE 5: FINAL VALIDATION & FORMATTING ===
        # Extract answer using regex to ensure proper format
        match = re.search(r"###FINAL_ANSWER:\s*([0-9,\s]+)###", final_answer)
        if match:
            raw_answer = match.group(1).replace(" ", "")
            # Validate each value is 3-digit integer
            values = raw_answer.split(",")
            validated = []
            for v in values:
                if v.isdigit() and 0 <= int(v) <= 999:
                    validated.append(v.zfill(3))  # Ensure 3-digit format
                else:
                    validated.append("000")  # Fallback
            return ",".join(validated)
        else:
            # Fallback if extraction fails
            return "000"