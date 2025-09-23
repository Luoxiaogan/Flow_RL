# Workflow ID: limr_153_0
# Benchmark: limr
# Data Indices: [284, 197]

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
        from collections import defaultdict

        # === PHASE 1: MULTI-PERSPECTIVE ANALYSIS (DIAMOND FORK) ===
        analysis_instructions = [
            """Analyze this problem from an ALGEBRAIC/ANALYTIC perspective:
            - Identify all variables, equations, and functional relationships
            - Look for symmetries, substitutions, or transformations that simplify the system
            - Propose solution strategies: elimination, substitution, matrix methods, etc.
            - Flag any constraints or domain restrictions
            - Output structured as: [Algebraic Insight]: ... [Strategy]: ...""",
            
            """Analyze this problem from a GEOMETRIC/VISUAL perspective:
            - Interpret any spatial, coordinate, or visual elements
            - Suggest coordinate systems, parametrizations, or geometric transformations
            - Identify invariants, symmetries, or proportional relationships
            - Propose solution strategies: distance formulas, vector methods, trigonometric identities
            - Output structured as: [Geometric Insight]: ... [Strategy]: ...""",
            
            """Analyze this problem from a COMBINATORIAL/NUMBER THEORETIC perspective:
            - Identify discrete structures, counting requirements, or modular constraints
            - Look for patterns, recurrences, or divisibility properties
            - Propose solution strategies: casework, generating functions, modular arithmetic
            - Flag any extremal or optimization aspects
            - Output structured as: [Combinatorial Insight]: ... [Strategy]: ...""",
            
            """Generate LATERAL/CREATIVE thinking approaches:
            - Propose at least 2 non-obvious transformations or analogies
            - Consider physical interpretations, dual problems, or invariant quantities
            - Suggest 'outside the box' substitutions or perspective shifts
            - Even if unlikely, include one 'wildcard' approach
            - Output structured as: [Creative Leap]: ... [Rationale]: ..."""
        ]

        analyses = await asyncio.gather(
            *[self.generate(instr, "") for instr in analysis_instructions]
        )

        # === PHASE 2: SYNTHESIZE UNIFIED PROBLEM UNDERSTANDING ===
        unified_understanding = await self.ensemble(
            instruction="""Synthesize a unified problem understanding:
            - Identify the dominant mathematical domain (algebra, geometry, combinatorics, etc.)
            - Preserve cross-domain insights that simplify the solution
            - Highlight the most promising solution strategy from each perspective
            - Flag any creative leaps that could unlock the problem
            - Output must include: [Domain]: ... [Core Insight]: ... [Recommended Strategy]: ...""",
            contexts_list=analyses
        )

        # === PHASE 3: STRUCTURED DECOMPOSITION ===
        decomposition = await self.decompose(
            instruction=f"""Decompose this problem using the following unified understanding:
            {unified_understanding}
            
            Guidelines:
            - Break into minimal, logically ordered subproblems
            - Each subproblem must be solvable independently given its dependencies
            - Include at least one verification step for critical calculations
            - Prioritize steps that unlock subsequent ones
            - Format each subproblem as: [Goal]: ... [Method]: ... [Verification]: ...""",
            context=unified_understanding
        )

        # === PHASE 4: SOLVE SUBPROBLEMS WITH DYNAMIC SCHEDULING ===
        solved_subproblems = {}
        subproblem_map = {sp['id']: sp for sp in decomposition}
        dependencies = defaultdict(set)
        reverse_deps = defaultdict(set)
        
        # Build dependency graph
        for sp in decomposition:
            deps = sp.get('dependencies', '').split(',') if sp.get('dependencies') else []
            deps = [d.strip() for d in deps if d.strip()]
            dependencies[sp['id']] = set(deps)
            for dep in deps:
                reverse_deps[dep].add(sp['id'])
        
        # Topological solve with parallelization
        ready = [sp_id for sp_id in subproblem_map.keys() if not dependencies[sp_id]]
        remaining = set(subproblem_map.keys())
        
        while remaining:
            current_batch = ready[:]
            ready = []
            
            # Solve current batch in parallel
            solve_tasks = []
            for sp_id in current_batch:
                sp = subproblem_map[sp_id]
                solve_tasks.append(self._solve_subproblem(sp, solved_subproblems))
            
            results = await asyncio.gather(*solve_tasks)
            for sp_id, result in zip(current_batch, results):
                solved_subproblems[sp_id] = result
                remaining.remove(sp_id)
                
                # Update ready list
                for depender in reverse_deps[sp_id]:
                    dependencies[depender].discard(sp_id)
                    if not dependencies[depender]:
                        ready.append(depender)
        
        # === PHASE 5: SYNTHESIZE FINAL ANSWER ===
        synthesis = await self.ensemble(
            instruction="""Assemble the final answer by logically chaining subproblem solutions:
            - Ensure dimensional consistency and unit alignment
            - Verify that all original constraints are satisfied
            - If multiple answer candidates exist, select the one best supported by verification steps
            - Output ONLY the final numerical answer as an integer between 000 and 999""",
            contexts_list=list(solved_subproblems.values())
        )

        # === PHASE 6: VALIDATE AND REVISE IF NEEDED ===
        for attempt in range(3):
            validation = await self.generate(
                instruction=f"""Validate this answer against the original problem:
                Answer: {synthesis}
                - Check consistency with all given equations/constraints
                - Verify dimensional/numerical reasonableness
                - Test boundary cases if applicable
                - Output 'VALID' if correct, or detailed error description if not""",
                context=synthesis
            )
            
            if "VALID" in validation.upper():
                break
                
            # Revise by re-solving the most likely faulty subproblem
            fault_analysis = await self.generate(
                instruction=f"""Identify the most likely faulty subproblem based on validation error:
                Validation: {validation}
                Subproblems: {list(solved_subproblems.items())}
                Output the ID of the subproblem to re-solve""",
                context=validation
            )
            
            # Extract subproblem ID (simple heuristic - improve in production)
            fault_id = None
            for sp_id in solved_subproblems.keys():
                if sp_id in fault_analysis:
                    fault_id = sp_id
                    break
            
            if fault_id:
                sp = subproblem_map[fault_id]
                solved_subproblems[fault_id] = await self._solve_subproblem(sp, solved_subproblems, enhanced=True)
                
                # Re-synthesize
                synthesis = await self.ensemble(
                    instruction="""Re-assemble final answer with revised subproblem:
                    - Incorporate the corrected subproblem solution
                    - Re-verify all constraints
                    - Output ONLY the final numerical answer as an integer between 000 and 999""",
                    contexts_list=list(solved_subproblems.values())
                )
            else:
                break  # Cannot identify fault - break to avoid infinite loop

        # === PHASE 7: FORMAT FINAL ANSWER ===
        final_answer = await self.generate(
            instruction=f"""Extract and format the final numerical answer:
            - Must be an integer between 000 and 999
            - Zero-pad to 3 digits if necessary
            - Remove any units or explanatory text
            - If multiple numbers, select the one that best fits the problem context
            Input: {synthesis}""",
            context=synthesis
        )
        
        # Extract first 3-digit number as fallback
        match = re.search(r'\b(\d{1,3})\b', final_answer)
        if match:
            num = int(match.group(1))
            if 0 <= num <= 999:
                return f"{num:03d}"
        
        return "000"  # Fallback

    async def _solve_subproblem(self, subproblem, solved_deps, enhanced=False):
        context = "\n".join([f"Subproblem {k}: {v}" for k, v in solved_deps.items()])
        
        base_instruction = f"""Solve this subproblem:
        {subproblem['description']}
        
        Dependencies (already solved):
        {context}
        
        Requirements:
        - Show all steps clearly
        - Include the verification method specified: {subproblem.get('verification', 'logical consistency')}
        - Output format: [Solution]: ... [Verification]: ..."""
        
        if enhanced:
            base_instruction += "\nENHANCED SCRUTINY: Double-check all calculations and consider alternative approaches."
        
        # Route to programmer if computational
        if any(kw in subproblem['description'].lower() for kw in ['calculate', 'compute', 'numerical', 'value of']):
            solution = await self.programmer(
                instruction=base_instruction,
                context=context
            )
        else:
            solution = await self.generate(base_instruction, context)
            # Add verification step
            solution = await self.revise(
                instruction="""Enhance this solution:
                - Add explicit verification step using the specified method
                - Check for calculation errors
                - Ensure logical flow is complete
                - Format as: [Solution]: ... [Verification]: ...""",
                context=solution
            )
        
        # Summarize to prevent context bloat
        return await self.summarize(
            instruction="Extract only the key result and verification status. Remove verbose steps.",
            context=solution
        )