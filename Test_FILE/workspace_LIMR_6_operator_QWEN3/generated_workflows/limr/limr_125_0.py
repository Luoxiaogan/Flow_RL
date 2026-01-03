# Workflow ID: limr_125_0
# Benchmark: limr
# Data Indices: [242, 236]

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

        # === PHASE 1: META-CLASSIFICATION & STRATEGY SELECTION ===
        classification = await self.generate(
            instruction="""Perform deep problem classification:
            1. Identify primary domain (combinatorics, number theory, geometry, algebra, probability)
            2. Detect secondary domains or cross-domain elements
            3. List applicable solution archetypes (e.g., generating functions, modular arithmetic, coordinate geometry, inclusion-exclusion)
            4. Estimate computational complexity (low/medium/high)
            5. Predict likely answer format and constraints (e.g., 000-999 integer)
            6. Flag potential traps or non-obvious insights
            Output as structured JSON with keys: domain, archetypes, complexity, constraints, traps""",
            context=""
        )

        # === PHASE 2: PARALLEL STRATEGY EXPLORATION ===
        strategy_contexts = await asyncio.gather(
            self.generate(
                instruction=f"""Develop COMBINATORIAL approach:
                - Apply counting principles, permutations, combinations
                - Consider casework, complementary counting, or recursive structures
                - Output must be self-contained with clear assumptions
                Classification context: {classification}""",
                context=""
            ),
            self.generate(
                instruction=f"""Develop ALGEBRAIC/NUMBER THEORETIC approach:
                - Look for equations, modular patterns, divisibility, or functional relationships
                - Consider polynomial roots, Diophantine constraints, or sequence properties
                - Output must be self-contained with clear assumptions
                Classification context: {classification}""",
                context=""
            ),
            self.generate(
                instruction=f"""Develop GEOMETRIC/PROBABILISTIC approach:
                - Apply spatial reasoning, coordinate systems, or probability distributions
                - Consider symmetry, expected value, or geometric probability
                - Output must be self-contained with clear assumptions
                Classification context: {classification}""",
                context=""
            )
        )

        # === PHASE 3: STRATEGY SYNTHESIS & ROADMAP GENERATION ===
        selected_strategy = await self.ensemble(
            instruction="""Select or synthesize the most promising solution path:
            Criteria:
            1. Mathematical rigor and completeness
            2. Computational feasibility
            3. Alignment with problem constraints
            4. Minimization of error-prone steps
            5. Elegance and insight leverage
            Output: Single coherent strategy narrative with explicit step-by-step plan""",
            contexts_list=strategy_contexts
        )

        # === PHASE 4: HIERARCHICAL DECOMPOSITION ===
        subproblems = await self.decompose(
            instruction=f"""Decompose selected strategy into minimal verifiable subproblems:
            Requirements:
            1. Each subproblem must have a clear input/output contract
            2. Dependencies must form a DAG (no cycles)
            3. Final subproblem must output an integer 000-999
            4. Include validation criteria for each subproblem
            Strategy context: {selected_strategy}""",
            context=selected_strategy
        )

        # === PHASE 5: PARALLEL SUBPROBLEM RESOLUTION ===
        subproblem_results = {}
        subproblem_queue = sorted(subproblems, key=lambda x: len(x.get('dependencies', '').split(',')) if x.get('dependencies') else 0)
        
        for sub in subproblem_queue:
            deps = [subproblem_results[dep_id.strip()] for dep_id in sub.get('dependencies', '').split(',') if dep_id.strip() in subproblem_results] if sub.get('dependencies') else []
            dep_context = "\n".join(deps) if deps else ""
            
            attempt = await self.generate(
                instruction=f"""Solve subproblem: {sub['description']}
                Context from dependencies: {dep_context}
                Requirements:
                - Show all work
                - State assumptions explicitly
                - Verify against validation criteria: {sub.get('validation', 'logical consistency')}
                - Output final result clearly labeled""",
                context=dep_context
            )
            
            # Adversarial revision loop
            for _ in range(3):
                critique = await self.generate(
                    instruction=f"""Critique this solution as a skeptical mathematician:
                    - Try to find logical flaws, calculation errors, or overlooked cases
                    - If no flaws found, state 'VERIFIED'
                    Solution: {attempt}""",
                    context=attempt
                )
                
                if "VERIFIED" in critique.upper():
                    break
                attempt = await self.revise(
                    instruction=f"""Revise based on critique: {critique}
                    Preserve correct elements, fix errors, add missing cases""",
                    context=attempt
                )
            
            subproblem_results[sub['id']] = attempt

        # === PHASE 6: FINAL SYNTHESIS & CANONICALIZATION ===
        final_synthesis = await self.ensemble(
            instruction="""Synthesize all subproblem results into final answer:
            1. Trace logical flow from subproblems to final result
            2. Resolve any inconsistencies
            3. Extract ONLY the final integer answer (000-999 format)
            4. If multiple candidates, select most rigorously derived
            5. ZERO-PAD to exactly three digits""",
            contexts_list=list(subproblem_results.values())
        )

        # === PHASE 7: COMPUTATIONAL VERIFICATION (if applicable) ===
        # Check if problem involves computation that can be code-verified
        needs_computation = await self.generate(
            instruction=f"""Determine if final answer can/should be verified via computation:
            - Look for enumerative, iterative, or large-number calculations
            - If yes, output Python code specification
            - If no, output 'NO COMPUTATION NEEDED'
            Final synthesis: {final_synthesis}""",
            context=final_synthesis
        )

        if "NO COMPUTATION NEEDED" not in needs_computation.upper():
            try:
                code_result = await self.programmer(
                    instruction=f"""Implement verification code:
                    - Compute final answer independently
                    - Include assertions for edge cases
                    - Output only the integer result
                    Specification: {needs_computation}
                    Expected answer: {final_synthesis}""",
                    context=final_synthesis,
                    max_retries=3
                )
                # Use code result if it matches format and is plausible
                match = re.search(r'\b\d{1,3}\b', code_result)
                if match:
                    final_answer = match.group(0).zfill(3)
                    return final_answer
            except Exception:
                pass  # Fall back to synthesized answer

        # Extract and format final answer
        final_answer_match = re.search(r'\b\d{1,3}\b', final_synthesis)
        if final_answer_match:
            return final_answer_match.group(0).zfill(3)
        
        # Fallback: return raw synthesis (shouldn't happen in well-formed problems)
        return final_synthesis.strip()[:3].zfill(3) if final_synthesis.strip()[:3].isdigit() else "000"