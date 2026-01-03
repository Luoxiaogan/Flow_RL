# Workflow ID: limr_29_0
# Benchmark: limr
# Data Indices: [51, 255]

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

        # STEP 1: CLASSIFY PROBLEM DOMAIN & STRATEGY
        classification = await self.generate(
            instruction="""Perform deep classification of this mathematical problem:
            1. Primary domain: Is this primarily Geometry, Number Theory, Algebra, Combinatorics, Probability, or Optimization?
            2. Secondary domains: Are there hybrid elements? (e.g., geometric combinatorics)
            3. Solution archetype: Proof-based, Calculation-heavy, Transformation-required, or Insight-dependent?
            4. Expected tools: Coordinate geometry? Modular arithmetic? Generating functions? Trigonometric identities?
            5. Confidence score: Rate your classification confidence 0-100 for each domain.
            6. Red flags: Any ambiguous conditions, missing constraints, or potential trick elements?
            Format as structured JSON with keys: primary_domain, secondary_domains, archetype, tools, confidence, red_flags""",
            context=""
        )

        # STEP 2: DOMAIN-SPECIFIC PARALLEL TRACKS
        domain = await self.summarize(
            instruction="Extract only the primary_domain from the classification JSON",
            context=classification
        )
        
        # Define domain-specific processing functions
        async def process_geometry():
            strategy = await self.generate(
                instruction=f"""Generate geometry-specific solution strategy:
                - Assign coordinate system or vector representations if applicable
                - Identify all given angles, lengths, perpendicularities, symmetries
                - Determine if trigonometric, vector, or synthetic geometry approach is optimal
                - Plan decomposition around angle chasing, triangle properties, or coordinate calculations
                Problem context: {self.problem_text}""",
                context=""
            )
            decomposition = await self.decompose(
                instruction=f"""Decompose using this geometry strategy:
                {strategy}
                Break into minimal atomic steps with clear dependencies. Prioritize angle/length relationships first.""",
                context=strategy
            )
            return await self.execute_decomposition(decomposition, "Geometry")

        async def process_number_theory():
            strategy = await self.generate(
                instruction=f"""Generate number theory strategy:
                - Identify all modular constraints, divisibility conditions, prime factors
                - Determine if Diophantine equations, Chinese Remainder Theorem, or Fermat's Little Theorem applies
                - Plan decomposition around equation solving, case analysis, or modular reduction
                Problem context: {self.problem_text}""",
                context=""
            )
            decomposition = await self.decompose(
                instruction=f"""Decompose using this number theory strategy:
                {strategy}
                Break into steps: equation setup → modular reduction → solution space enumeration → validation""",
                context=strategy
            )
            return await self.execute_decomposition(decomposition, "Number Theory")

        async def process_algebra():
            strategy = await self.generate(
                instruction=f"""Generate algebra strategy:
                - Identify polynomial degrees, functional equations, or complex number operations
                - Determine if substitution, symmetry exploitation, or coefficient matching is optimal
                - Plan decomposition around variable isolation, equation transformation, or root analysis
                Problem context: {self.problem_text}""",
                context=""
            )
            decomposition = await self.decompose(
                instruction=f"""Decompose using this algebra strategy:
                {strategy}
                Break into: expression simplification → equation setup → solution derivation → verification""",
                context=strategy
            )
            return await self.execute_decomposition(decomposition, "Algebra")

        async def process_combinatorics():
            strategy = await self.generate(
                instruction=f"""Generate combinatorics strategy:
                - Identify independent choices, symmetries, overcounting risks
                - Determine if permutations, combinations, inclusion-exclusion, or generating functions apply
                - Plan decomposition around case breakdown, counting principle application, boundary condition handling
                Problem context: {self.problem_text}""",
                context=""
            )
            decomposition = await self.decompose(
                instruction=f"""Decompose using this combinatorics strategy:
                {strategy}
                Break into: case identification → counting method selection → calculation → adjustment for overcounting""",
                context=strategy
            )
            return await self.execute_decomposition(decomposition, "Combinatorics")

        # STEP 3: EXECUTE DOMAIN TRACKS IN PARALLEL (CONFIDENCE-AWARE)
        domain_lower = domain.lower()
        tasks = []
        
        if "geometry" in domain_lower:
            tasks.append(process_geometry())
        if "number" in domain_lower or "theory" in domain_lower:
            tasks.append(process_number_theory())
        if "algebra" in domain_lower:
            tasks.append(process_algebra())
        if "combin" in domain_lower or "probab" in domain_lower:
            tasks.append(process_combinatorics())
        
        # If no high-confidence domain, run all
        if len(tasks) == 0:
            tasks = [process_geometry(), process_number_theory(), process_algebra(), process_combinatorics()]
        
        # Execute in parallel
        results = await asyncio.gather(*tasks, return_exceptions=True)
        valid_results = [r for r in results if isinstance(r, str) and len(r.strip()) > 0]

        # STEP 4: ENSEMBLE SYNTHESIS
        if len(valid_results) == 0:
            # Fallback: direct solve
            final_answer = await self.generate(
                instruction="""Solve directly with maximum rigor:
                - Show all steps
                - Verify each calculation
                - Box final answer as integer between 000-999
                - If multiple answers possible, explain why and select most plausible""",
                context=""
            )
        else:
            final_answer = await self.ensemble(
                instruction="""Synthesize the best answer from all domain-specific solutions:
                1. Evaluate each solution for logical completeness and step-by-step rigor
                2. Prefer solutions with explicit verification steps
                3. If answers conflict, trace back to first divergence point and re-evaluate
                4. Final output must be a single integer between 000 and 999
                5. If no solution is fully consistent, return the most mathematically sound partial answer""",
                contexts_list=valid_results
            )

        # STEP 5: VALIDATION CASCADE
        for validation_round in range(2):  # Max 2 iterations
            # Numerical sanity check
            sanity_check = await self.programmer(
                instruction=f"""Validate this answer numerically:
                Answer: {final_answer}
                Write code to verify against original problem constraints.
                Return 'VALID' if passes, 'INVALID: [reason]' if fails.
                If answer not computable, return 'UNCERTAIN'.""",
                context=final_answer
            )
            
            if "INVALID" in sanity_check:
                # Trigger revision with specific feedback
                final_answer = await self.revise(
                    instruction=f"""Revise solution based on validation failure:
                    Validation result: {sanity_check}
                    Re-examine all assumptions. Check for:
                    - Arithmetic errors
                    - Misinterpreted constraints
                    - Domain misapplication
                    - Boundary condition violations
                    Output revised integer answer 000-999.""",
                    context=final_answer
                )
            elif "VALID" in sanity_check:
                break
            else:
                # Uncertain - try logical validation
                logical_check = await self.generate(
                    instruction=f"""Perform logical consistency check:
                    Does this answer {final_answer} satisfy all problem conditions?
                    Are there any contradictions in the derivation?
                    Return 'CONSISTENT' or 'INCONSISTENT: [reason]'""",
                    context=final_answer
                )
                if "INCONSISTENT" in logical_check:
                    final_answer = await self.revise(
                        instruction=f"""Fix logical inconsistency:
                        {logical_check}
                        Re-derive from first principles. Output revised integer 000-999.""",
                        context=final_answer
                    )
                else:
                    break

        # STEP 6: FINAL FORMATTING & BOUNDARY CHECK
        formatted_answer = await self.revise(
            instruction="""Ensure final answer is:
            - A single integer between 000 and 999
            - No units, no explanations, no text
            - If multiple digits, zero-padded to 3 digits (e.g., 42 → 042)
            - If answer invalid, return 000 as fallback
            Extract ONLY the integer.""",
            context=final_answer
        )

        # Extract integer with regex as final safeguard
        match = re.search(r'\b(0\d{2}|[1-9]\d{0,2})\b', formatted_answer)
        if match:
            return match.group(1).zfill(3)
        else:
            return "000"  # Ultimate fallback

    async def execute_decomposition(self, decomposition, domain_name):
        """Execute a decomposition plan step by step"""
        results = []
        dependency_graph = {step['id']: step for step in decomposition}
        
        # Topological sort by dependencies (simplified)
        ordered_steps = []
        remaining = list(decomposition)
        
        while remaining:
            for step in remaining[:]:
                deps = step.get('dependencies', '').split(',') if step.get('dependencies') else []
                if all(d.strip() in [s['id'] for s in ordered_steps] for d in deps if d.strip()):
                    ordered_steps.append(step)
                    remaining.remove(step)
                    break
            else:
                # Circular dependency or missing deps - take first remaining
                ordered_steps.append(remaining.pop(0))
        
        # Execute steps in order
        for step in ordered_steps:
            step_result = await self.generate(
                instruction=f"""Execute this {domain_name} subproblem:
                {step['description']}
                Show all work. If calculation needed, use programmer operator internally.
                Be precise and rigorous. Output only the result of this step.""",
                context="\n".join(results[-3:]) if results else ""  # Last 3 results as context
            )
            results.append(f"Step {step['id']}: {step_result}")
        
        # Synthesize final answer from steps
        synthesis = await self.generate(
            instruction=f"""Synthesize final answer from these {domain_name} steps:
            {' '.join(results)}
            Derive the single integer answer 000-999. Show final calculation if needed.""",
            context="\n".join(results)
        )
        return synthesis