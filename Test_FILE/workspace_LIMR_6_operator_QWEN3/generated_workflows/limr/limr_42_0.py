# Workflow ID: limr_42_0
# Benchmark: limr
# Data Indices: [164, 273]

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
        import json

        # === PHASE 1: META-COGNITIVE ANALYSIS ===
        # Extract problem type, constraints, entities, and solution strategies
        problem_analysis = await self.generate(
            instruction="""Perform a deep forensic analysis of this mathematical problem. Address:

1. Problem Classification: Which mathematical domain(s) does this belong to? (e.g., algebra, combinatorics, number theory, geometry, probability)
2. Key Entities: List all variables, constants, functions, and objects mentioned.
3. Constraints & Conditions: Identify explicit and implicit constraints (e.g., integer solutions, positivity, symmetry).
4. Solution Strategies: Propose 3-5 potential high-level approaches (e.g., Vieta's formulas, inclusion-exclusion, coordinate geometry, generating functions).
5. Known Analogues: Reference any similar problems or theorems that might apply.
6. Answer Format: Confirm expected output (integer 000-999) and any units or special formatting.

Structure your response clearly with numbered sections. Be exhaustive — do not skip any component.""",
            context=""
        )

        # === PHASE 2: HIERARCHICAL DECOMPOSITION ===
        # Break into subproblems with dependencies
        subproblems = await self.decompose(
            instruction="""Decompose this problem into a hierarchy of subproblems. For each:

- Provide a clear, self-contained description.
- Specify dependencies (which subproblems must be solved first).
- Tag each subproblem by type: 'COMPUTATIONAL' (requires calculation), 'CONCEPTUAL' (requires proof/insight), or 'VALIDATION' (checking constraints).

Prioritize subproblems that unlock others. Include at least one validation subproblem to check final answer against constraints.""",
            context=problem_analysis
        )

        # === PHASE 3: DYNAMIC ROUTING & PARALLEL EXECUTION ===
        # Route each subproblem to appropriate operator based on type
        subproblem_results = {}
        subproblem_tasks = []

        for sp in subproblems:
            sp_id = sp['id']
            sp_desc = sp['description']
            sp_type = "COMPUTATIONAL" if "COMPUTATIONAL" in sp_desc.upper() else "CONCEPTUAL"

            if sp_type == "COMPUTATIONAL":
                # Route to Programmer with strict precision instructions
                task = self.programmer(
                    instruction=f"""Solve this computational subproblem exactly:

{sp_desc}

Requirements:
- Use symbolic computation (SymPy) where possible.
- Avoid floating-point arithmetic; use fractions or integers.
- Validate result against constraints from problem_analysis.
- Output only the final answer as an integer (000-999 format if applicable).""",
                    context=problem_analysis
                )
            else:
                # Route to Generate for conceptual/proof-based subproblems
                task = self.generate(
                    instruction=f"""Solve this conceptual subproblem:

{sp_desc}

Requirements:
- Show all logical steps.
- Reference relevant theorems or identities.
- Connect back to original problem constraints.
- If stuck, propose 2 alternative approaches.""",
                    context=problem_analysis
                )
            
            # Store task with ID for dependency resolution
            subproblem_tasks.append((sp_id, task))

        # Execute all subproblems in parallel
        results = await asyncio.gather(*[task for _, task in subproblem_tasks])
        for i, (sp_id, _) in enumerate(subproblem_tasks):
            subproblem_results[sp_id] = results[i]

        # === PHASE 4: SYNTHESIS & ENSEMBLE ===
        # Combine subproblem results into candidate solutions
        candidate_solutions = []
        for sp_id, result in subproblem_results.items():
            # Create solution candidate by combining with analysis
            candidate = await self.generate(
                instruction=f"""Integrate this subproblem result into a complete solution:

Subproblem Result: {result}

Context: {problem_analysis}

Produce a complete, end-to-end solution that:
1. Starts from first principles.
2. Shows all intermediate steps.
3. Explicitly checks against all constraints.
4. Outputs final answer as integer (000-999).""",
                context=result
            )
            candidate_solutions.append(candidate)

        # Ensemble: Select best or synthesize
        final_solution = await self.ensemble(
            instruction="""Evaluate all candidate solutions and select the best one based on:

1. Mathematical rigor (no gaps in logic).
2. Completeness (addresses all constraints).
3. Precision (exact integer answer, no approximation).
4. Elegance (minimal unnecessary steps).

If multiple solutions are valid, synthesize them into a unified answer. Output ONLY the final integer answer (000-999 format).""",
            contexts_list=candidate_solutions
        )

        # === PHASE 5: ADVERSARIAL VALIDATION & REFINEMENT ===
        # Challenge the solution
        critique = await self.generate(
            instruction=f"""Play devil's advocate. Critique this solution:

{final_solution}

Look for:
- Hidden assumptions.
- Edge cases not considered.
- Arithmetic or algebraic errors.
- Violations of constraints.

If no flaws found, output 'VALID'. Otherwise, list specific critiques.""",
            context=final_solution
        )

        if "VALID" not in critique.upper():
            # Revise based on critique
            final_solution = await self.revise(
                instruction=f"""Revise the solution to address these critiques:

{critique}

Requirements:
- Maintain exact integer output.
- Show corrected steps explicitly.
- Re-validate against all original constraints.""",
                context=final_solution
            )

        # === PHASE 6: FINAL EXTRACTION & FORMATTING ===
        # Ensure output is clean integer
        answer = await self.programmer(
            instruction="""Extract the final integer answer from this solution text. The answer must be an integer between 000 and 999.

If multiple numbers appear, select the one that is the final answer to the original problem.

Output ONLY the integer, zero-padded to 3 digits (e.g., '042', '123').""",
            context=final_solution,
            max_retries=3
        )

        return answer.strip()