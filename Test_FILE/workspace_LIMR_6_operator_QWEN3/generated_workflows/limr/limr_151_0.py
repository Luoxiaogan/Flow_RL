# Workflow ID: limr_151_0
# Benchmark: limr
# Data Indices: [126, 62]

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
        from typing import Dict, List, Any

        # === PHASE 1: PARALLEL STRATEGIC HYPOTHESIS GENERATION ===
        hypothesis_instructions = [
            """Analyze this problem from an ALGEBRAIC perspective:
            - Identify all variables, equations, and functional relationships.
            - What algebraic manipulations or substitutions could simplify it?
            - Are there symmetries, invariants, or identities to exploit?
            - What are the potential pitfalls or misleading paths?
            - Outline a 3-step algebraic solution strategy if possible.""",
            
            """Analyze this problem from a COMBINATORIAL/LOGICAL perspective:
            - Are there discrete cases, counting principles, or logical conditions?
            - Could it be modeled as a graph, set, or probability space?
            - What boundary conditions or integer constraints exist?
            - Would case analysis or pigeonhole principle apply?
            - Outline a 3-step combinatorial solution strategy if possible.""",
            
            """Analyze this problem from a GEOMETRIC/VISUAL perspective:
            - Can it be represented spatially or with diagrams?
            - Are there symmetries, transformations, or invariants in space?
            - Would coordinate geometry, vectors, or trigonometry help?
            - What geometric theorems or properties might be relevant?
            - Outline a 3-step geometric solution strategy if possible.""",
            
            """Analyze this problem from a NUMBER THEORETIC perspective:
            - Are there divisibility, modular arithmetic, or prime factorization aspects?
            - Could Diophantine equations, gcd/lcm, or congruences be involved?
            - What are the constraints on integer or rational solutions?
            - Would Fermat's little theorem, Euler's theorem, or Chinese remainder help?
            - Outline a 3-step number-theoretic solution strategy if possible.""",
            
            """Analyze this problem from an OPTIMIZATION/CALCULUS perspective:
            - Is there a function to maximize/minimize?
            - Are there constraints that suggest Lagrange multipliers or inequalities?
            - Would derivatives, AM-GM, Cauchy-Schwarz, or Jensen's inequality apply?
            - What are the critical points or boundary behaviors?
            - Outline a 3-step optimization solution strategy if possible."""
        ]

        hypotheses = await asyncio.gather(
            *[self.generate(instruction=instr, context="") for instr in hypothesis_instructions]
        )

        # === PHASE 2: STRATEGY SYNTHESIS & ROADMAP GENERATION ===
        strategy_roadmap = await self.ensemble(
            instruction="""Synthesize the above analyses into a unified solution roadmap:
            - Identify the MOST PROMISING primary approach (algebraic, combinatorial, etc.)
            - Note any critical insights or tools from secondary approaches to incorporate
            - Flag any contradictions or conflicting assumptions between analyses
            - Outline a step-by-step master plan with 3-5 key phases
            - For each phase, specify: what operator(s) to use, what context is needed, and success criteria
            - Include fallback strategies if primary path fails
            Output in structured markdown with clear section headers.""",
            contexts_list=hypotheses
        )

        # === PHASE 3: HIERARCHICAL TASK DECOMPOSITION ===
        decomposition = await self.decompose(
            instruction=f"""Decompose the problem into atomic subproblems using this strategy roadmap:
            {strategy_roadmap}
            
            Requirements:
            - Each subproblem must be SOLVABLE in isolation given its dependencies
            - Specify DEPENDENCIES clearly (which subproblem IDs must be solved first)
            - Tag each subproblem with MODALITY: [symbolic, numeric, logical, geometric, etc.]
            - Include EXPECTED OUTPUT FORMAT for each (equation, integer, set, etc.)
            - Maximum 7 subproblems; if more are needed, group related steps
            - Prioritize parallelizability: minimize unnecessary dependencies""",
            context=strategy_roadmap
        )

        # === PHASE 4: DEPENDENCY-AWARE SUBPROBLEM SOLVING ===
        solved_subproblems: Dict[str, str] = {}
        subproblem_map = {sp['id']: sp for sp in decomposition}

        # Group subproblems by dependency depth (topological sort simulation)
        unsolved = set(subproblem_map.keys())
        solved_set = set()
        
        while unsolved:
            # Find subproblems whose dependencies are all solved
            current_batch = []
            for sp_id in list(unsolved):
                deps = subproblem_map[sp_id].get('dependencies', '').split(',') if subproblem_map[sp_id].get('dependencies') else []
                deps = [d.strip() for d in deps if d.strip()]
                if all(dep in solved_set for dep in deps):
                    current_batch.append(sp_id)
            
            if not current_batch:
                # Circular dependency or unsolvable - break with error
                break

            # Solve current batch in parallel
            async def solve_subproblem(sp_id: str) -> tuple:
                sp = subproblem_map[sp_id]
                context_str = "\n".join([f"Subproblem {dep}: {solved_subproblems[dep]}" 
                                       for dep in sp.get('dependencies', '').split(',') 
                                       if dep.strip() and dep in solved_subproblems])
                
                modality = sp.get('modality', 'symbolic').lower()
                
                if 'numeric' in modality or 'calculation' in modality:
                    solution = await self.programmer(
                        instruction=f"""Solve this subproblem with precise computation:
                        Subproblem: {sp['description']}
                        Dependencies: {context_str}
                        Expected output format: {sp.get('output_format', 'integer')}
                        - Use exact arithmetic, no floating point approximations
                        - Validate boundary conditions
                        - Output ONLY the final answer in specified format""",
                        context=context_str
                    )
                else:
                    solution = await self.generate(
                        instruction=f"""Solve this subproblem with rigorous reasoning:
                        Subproblem: {sp['description']}
                        Modality: {modality}
                        Dependencies: {context_str}
                        Expected output format: {sp.get('output_format', 'mathematical expression')}
                        - Show key steps but be concise
                        - Justify non-obvious moves
                        - Cross-check with dependency results if applicable""",
                        context=context_str
                    )
                    # Revise for rigor
                    solution = await self.revise(
                        instruction="""Improve this solution:
                        - Fill any logical gaps
                        - Add missing justifications
                        - Ensure mathematical precision
                        - Format final answer clearly""",
                        context=solution
                    )
                
                return sp_id, solution

            batch_results = await asyncio.gather(
                *[solve_subproblem(sp_id) for sp_id in current_batch]
            )
            
            for sp_id, solution in batch_results:
                solved_subproblems[sp_id] = solution
                solved_set.add(sp_id)
                unsolved.remove(sp_id)

        # === PHASE 5: CROSS-VALIDATION & CONSISTENCY CHECK ===
        validation_context = "\n".join([f"Subproblem {sp_id}: {result}" 
                                      for sp_id, result in solved_subproblems.items()])
        
        consistency_report = await self.generate(
            instruction=f"""Perform cross-validation of all subproblem solutions:
            {validation_context}
            
            Check for:
            - Numerical consistency (e.g., if Subproblem 1 says x=5, does Subproblem 3 respect that?)
            - Logical consistency (no contradictory assumptions)
            - Boundary condition adherence
            - Units/dimensions consistency if applicable
            - Identify any discrepancies or potential errors
            Output a bullet-point validation report.""",
            context=validation_context
        )

        # If inconsistencies found, trigger revision
        if "inconsistency" in consistency_report.lower() or "error" in consistency_report.lower():
            solved_subproblems_str = "\n".join([f"{k}: {v}" for k,v in solved_subproblems.items()])
            revised_solutions = await self.revise(
                instruction=f"""Revise solutions to resolve inconsistencies:
                Validation Report: {consistency_report}
                Current Solutions: {solved_subproblems_str}
                
                - Modify only what's necessary to fix inconsistencies
                - Preserve correct parts
                - Re-verify dependencies after changes
                - Output revised solutions in same format""",
                context=solved_subproblems_str
            )
            # Simple update - in practice, would re-parse and update specific subproblems
            # For simplicity, we'll treat this as a full revision
            validation_context = revised_solutions

        # === PHASE 6: FINAL SYNTHESIS & ANSWER EXTRACTION ===
        final_answer = await self.ensemble(
            instruction=f"""Synthesize final answer from validated subproblem solutions:
            {validation_context}
            
            Requirements:
            - Extract the FINAL NUMERICAL ANSWER (integer between 000 and 999)
            - If multiple answers, sum them or follow problem's aggregation instruction
            - If answer is not integer, derive integer form (e.g., floor, count, index)
            - JUSTIFY how you arrived at the final integer
            - Format output as: "FINAL_ANSWER: XXX" where XXX is 3-digit integer
            - If uncertain, use fallback strategy from roadmap""",
            contexts_list=[validation_context]
        )

        # Extract final answer with regex fallback
        match = re.search(r"FINAL_ANSWER:\s*(\d{1,3})", final_answer)
        if match:
            answer = int(match.group(1))
            # Ensure 3-digit format
            return f"{answer:03d}"
        else:
            # Fallback: extract any 1-3 digit number
            numbers = re.findall(r"\b\d{1,3}\b", final_answer)
            if numbers:
                answer = int(numbers[-1])  # Last number as most likely final answer
                return f"{answer:03d}"
            else:
                # Ultimate fallback: return 000 (should trigger review)
                return "000"