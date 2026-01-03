# Workflow ID: limr_31_0
# Benchmark: limr
# Data Indices: [18, 192]

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

        # === PHASE 1: META-CLASSIFICATION & STRATEGY PROBING ===
        classification = await self.generate(
            instruction="""Perform deep problem classification:
            1. Identify primary domain (algebra, geometry, combinatorics, number theory, etc.)
            2. Extract all variables, constants, and target expressions
            3. List explicit and implicit constraints
            4. Predict likely solution strategies (e.g., generating functions, modular arithmetic, coordinate geometry)
            5. Flag any deceptive elements or potential traps
            Format as structured JSON-like text with clear section headers.""",
            context=""
        )

        # Spawn parallel strategy probes
        strategy_probes = await asyncio.gather(
            self.generate(
                instruction=f"""Strategy Probe 1 - Algebraic Lens:
                Given classification: {classification}
                Attempt to reframe the problem using algebraic manipulation, equation setup, or polynomial identities.
                Outline steps without full computation. Identify if this approach is tractable.""",
                context=""
            ),
            self.generate(
                instruction=f"""Strategy Probe 2 - Combinatorial/Number Theoretic Lens:
                Given classification: {classification}
                Explore combinatorial interpretations, counting arguments, modular arithmetic, or divisibility properties.
                Can the problem be reduced to counting, probability, or residue classes?""",
                context=""
            ),
            self.generate(
                instruction=f"""Strategy Probe 3 - Geometric/Structural Lens:
                Given classification: {classification}
                If applicable, model using coordinates, vectors, symmetry, or invariant properties.
                Identify geometric transformations or structural simplifications.""",
                context=""
            ),
            self.generate(
                instruction=f"""Strategy Probe 4 - Computational/Algorithmic Lens:
                Given classification: {classification}
                Design a brute-force or optimized algorithm to compute the answer.
                Estimate complexity and feasibility within reasonable bounds.""",
                context=""
            )
        )

        # Validate and refine each probe
        validated_probes = await asyncio.gather(
            *[self.revise(
                instruction="""Critique this strategy probe:
                - Is the mathematical foundation sound?
                - Are there hidden assumptions or potential errors?
                - Does it respect all problem constraints?
                - What is its computational or conceptual complexity?
                Return 'VALID' if promising, 'INVALID' if flawed, with brief justification.""",
                context=probe
            ) for probe in strategy_probes]
        )

        # Synthesize best strategy or hybrid approach
        strategy_synthesis = await self.ensemble(
            instruction="""Synthesize a master solution strategy:
            - Combine the most promising elements from valid probes
            - Resolve conflicts or contradictions between approaches
            - Prioritize strategies that minimize computational complexity
            - Ensure the approach leads to an exact integer answer 000-999
            Output a step-by-step solution roadmap.""",
            contexts_list=[f"Probe {i+1}: {probe}" for i, probe in enumerate(validated_probes)]
        )

        # === PHASE 2: HIERARCHICAL DECOMPOSITION ===
        decomposition = await self.decompose(
            instruction=f"""Decompose the problem using this strategy: {strategy_synthesis}
            Break into atomic, sequentially dependent subproblems.
            Each subproblem must be solvable in isolation given its dependencies.
            Format: clear description, prerequisite subproblem IDs, expected output type.""",
            context=""
        )

        # Topological sort of subproblems (simplified for DAG)
        subproblem_order = []
        unresolved = {sp['id']: sp for sp in decomposition}
        while unresolved:
            ready = [sp_id for sp_id, sp in unresolved.items() 
                    if not sp['dependencies'] or all(dep in subproblem_order for dep in sp['dependencies'].split(','))]
            if not ready:
                break  # Circular dependency (shouldn't happen in well-formed problems)
            next_sp = ready[0]
            subproblem_order.append(next_sp)
            del unresolved[next_sp]

        # === PHASE 3: SUBPROBLEM SOLVING WITH TRIPLE VERIFICATION ===
        solutions = {}
        for sp_id in subproblem_order:
            sp = next(item for item in decomposition if item['id'] == sp_id)
            
            # Parallel solution attempts: symbolic, computational, verification
            symbolic_attempt = await self.generate(
                instruction=f"""Solve subproblem symbolically:
                Subproblem: {sp['description']}
                Dependencies: {[solutions[dep] for dep in sp['dependencies'].split(',') if dep in solutions] if sp['dependencies'] else []}
                Derive exact solution using algebra, calculus, or combinatorial reasoning. Show steps.""",
                context=str(solutions)
            )
            
            computational_attempt = await self.programmer(
                instruction=f"""Solve subproblem computationally:
                Subproblem: {sp['description']}
                Dependencies: {[solutions[dep] for dep in sp['dependencies'].split(',') if dep in solutions] if sp['dependencies'] else []}
                Write Python code to compute exact answer. Handle edge cases. Return only final value.""",
                context=str(solutions),
                max_retries=2
            )
            
            verification_attempt = await self.revise(
                instruction=f"""Verify subproblem solution:
                Subproblem: {sp['description']}
                Symbolic: {symbolic_attempt}
                Computational: {computational_attempt}
                Check for consistency, dimensional correctness, and constraint satisfaction.
                If discrepancy, diagnose root cause.""",
                context=f"Symbolic: {symbolic_attempt}\nComputational: {computational_attempt}"
            )

            # Ensemble to resolve discrepancies
            subproblem_solution = await self.ensemble(
                instruction="""Resolve subproblem solution:
                - If symbolic and computational agree, accept result
                - If conflict, prefer computational if exact and within bounds
                - If both flawed, return 'RETRY' to trigger re-decomposition
                Output final answer for this subproblem only.""",
                contexts_list=[symbolic_attempt, computational_attempt, verification_attempt]
            )
            
            if "RETRY" in subproblem_solution:
                # Trigger meta-revision and re-decompose
                revision = await self.generate(
                    instruction=f"""Subproblem {sp_id} failed verification. Diagnose:
                    - Is the decomposition flawed?
                    - Are dependencies incorrectly specified?
                    - Is the master strategy inappropriate?
                    Propose corrected decomposition or strategy.""",
                    context=f"Subproblem: {sp}\nAttempts: {symbolic_attempt}, {computational_attempt}, {verification_attempt}"
                )
                # Simplified retry: re-run with revised context (in practice, might re-trigger full workflow)
                subproblem_solution = await self.generate(
                    instruction=f"Re-solve with revised approach: {revision}",
                    context=str(solutions)
                )
            
            solutions[sp_id] = subproblem_solution

        # === PHASE 4: FINAL ANSWER EXTRACTION & FORMATTING ===
        final_answer_draft = await self.generate(
            instruction=f"""Extract final numerical answer:
            Based on all subproblem solutions: {solutions}
            Compute the final result as an integer between 0 and 999.
            If outside range, apply modulo 1000 or diagnose error.
            Justify why this is the correct contest answer.""",
            context=str(solutions)
        )

        formatted_answer = await self.programmer(
            instruction="""Validate and format answer:
            Input: a proposed numerical answer
            Steps:
            1. Convert to integer
            2. Ensure 0 <= answer <= 999
            3. Format as three-digit string with leading zeros
            4. Return ONLY the three-digit string
            Example: 7 → "007", 123 → "123", 1001 → "001" (if modulo applied)""",
            context=final_answer_draft,
            max_retries=1
        )

        # Final sanity check
        clean_answer = re.sub(r'\D', '', formatted_answer)
        if len(clean_answer) > 3:
            clean_answer = clean_answer[-3:]
        elif len(clean_answer) < 3:
            clean_answer = clean_answer.zfill(3)
        
        return clean_answer[:3]  # Ensure exactly 3 digits