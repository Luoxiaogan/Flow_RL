# Workflow ID: limr_30_0
# Benchmark: limr
# Data Indices: [307, 43]

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

        # STEP 1: PARALLEL PROBLEM CLASSIFICATION
        classification_instructions = [
            """Analyze this problem through an ALGEBRAIC lens:
            - Identify variables, equations, and functional relationships.
            - Determine if it involves polynomials, sequences, inequalities, or functional equations.
            - Suggest 2-3 algebraic strategies (e.g., substitution, generating functions, induction).
            - Flag any algebraic pitfalls (e.g., division by zero, convergence issues).""",
            
            """Analyze this problem through a GEOMETRIC/ANALYTIC lens:
            - Identify shapes, coordinates, distances, angles, or transformations.
            - Determine if it requires coordinate geometry, vector methods, or properties of conics.
            - Suggest 2-3 geometric strategies (e.g., coordinate placement, symmetry, parametric forms).
            - Flag any geometric assumptions (e.g., planar vs 3D, orientation).""",
            
            """Analyze this problem through a COMBINATORIAL/NUMBER THEORETIC lens:
            - Identify counting elements, modular constraints, divisibility, or recursive structures.
            - Determine if it involves permutations, modular arithmetic, prime properties, or recurrence.
            - Suggest 2-3 combinatorial/NT strategies (e.g., generating functions, modular reduction, bijection).
            - Flag any combinatorial traps (e.g., overcounting, boundary conditions)."""
        ]

        classification_results = await asyncio.gather(
            *[self.generate(instr, "") for instr in classification_instructions]
        )

        # Ensemble classifications into a unified strategic roadmap
        roadmap = await self.ensemble(
            instruction="""Synthesize these parallel analyses into a unified problem-solving roadmap:
            1. What is the PRIMARY problem type? (Algebra, Geometry, Combinatorics, etc.)
            2. What are the 2 MOST PROMISING solution strategies? Be specific.
            3. Are there any critical constraints, assumptions, or pitfalls to avoid?
            4. Does this problem require decomposition into subproblems? (Yes/No)
            5. What verification methods are feasible (e.g., numerical check, symmetry, edge case)?
            Output in structured JSON-like format with keys: type, strategies, pitfalls, decompose, verification.""",
            contexts_list=classification_results
        )

        # STEP 2: CONDITIONAL DECOMPOSITION
        needs_decomposition = "yes" in roadmap.lower() and "decompose" in roadmap.lower()
        subproblem_results = {}
        
        if needs_decomposition:
            decomposition = await self.decompose(
                instruction="""Break this problem into minimal, solvable subproblems:
                - Each subproblem should be self-contained with clear inputs/outputs.
                - Specify dependencies between subproblems (which must be solved first).
                - Focus on mathematical modularity (e.g., 'first prove lemma X', 'then compute Y').
                - Maximum 5 subproblems; prioritize critical path.""",
                context=roadmap
            )
            
            # Solve subproblems in dependency order
            solved_ids = set()
            for _ in range(len(decomposition)):  # Safety limit
                for sub in decomposition:
                    deps = sub.get('dependencies', '').split(',') if sub.get('dependencies') else []
                    if all(d.strip() in solved_ids for d in deps) and sub['id'] not in solved_ids:
                        # Solve this subproblem
                        sub_solution = await self.generate(
                            instruction=f"""Solve this subproblem as part of the larger solution:
                            Subproblem: {sub['description']}
                            Context: {roadmap}
                            - Show all steps clearly.
                            - Box the final result for this subproblem.
                            - If stuck, propose an alternative approach.""",
                            context=""
                        )
                        subproblem_results[sub['id']] = sub_solution
                        solved_ids.add(sub['id'])
            
            # Summarize subproblem results for main solution
            sub_summary = await self.summarize(
                instruction="Condense all subproblem solutions into a coherent summary for final integration.",
                context="\n\n".join(f"Subproblem {k}: {v}" for k, v in subproblem_results.items())
            )
        else:
            sub_summary = ""

        # STEP 3: PARALLEL SOLUTION ATTEMPTS (DIAMOND PATTERN)
        solution_instructions = [
            f"""Attempt 1: Solve using PRIMARY STRATEGY from roadmap.
            Roadmap: {roadmap}
            Subproblem Summary: {sub_summary}
            - Follow the recommended approach rigorously.
            - Show all mathematical steps.
            - Explicitly state any assumptions.
            - End with: "FINAL ANSWER: \\boxed{{XXX}}" where XXX is 000-999.""",
            
            f"""Attempt 2: Solve using ALTERNATE STRATEGY (be creative).
            Roadmap: {roadmap}
            Subproblem Summary: {sub_summary}
            - Choose a different mathematical lens or technique.
            - If primary is algebraic, try combinatorial or geometric.
            - Include verification step (e.g., 'Check with n=1,2,3').
            - End with: "FINAL ANSWER: \\boxed{{XXX}}".""",
            
            f"""Attempt 3: Computational/Algorithmic approach.
            Roadmap: {roadmap}
            Subproblem Summary: {sub_summary}
            - Translate problem into code or algorithm.
            - Use numerical methods, simulation, or symbolic computation.
            - If applicable, generate pseudocode or Python snippet.
            - End with: "FINAL ANSWER: \\boxed{{XXX}}"."""
        ]

        solution_attempts = await asyncio.gather(
            *[self.generate(instr, "") for instr in solution_instructions]
        )

        # STEP 4: PROGRAMMATIC VERIFICATION (WHERE POSSIBLE)
        verified_attempts = []
        for i, attempt in enumerate(solution_attempts):
            # Extract boxed answer for verification
            box_match = re.search(r"\\boxed\{(\d{3})\}", attempt)
            if box_match:
                candidate_answer = box_match.group(1)
                # Generate verification code if roadmap suggests it's feasible
                if "numerical" in roadmap.lower() or "computation" in roadmap.lower() or "code" in attempt.lower():
                    try:
                        verification = await self.programmer(
                            instruction=f"""Verify the answer {candidate_answer} for this problem:
                            Original attempt: {attempt[:500]}...
                            - Write code to independently compute or validate the result.
                            - If validation fails, output "INVALID: [reason]".
                            - If valid, output "VALID: {candidate_answer}".""",
                            context=attempt,
                            max_retries=2
                        )
                        if "VALID" in verification:
                            verified_attempts.append(attempt)
                        else:
                            # Keep attempt but mark as unverified
                            verified_attempts.append(attempt + f"\n\n[UNVERIFIED: {verification}]")
                    except Exception:
                        verified_attempts.append(attempt + "\n\n[VERIFICATION FAILED]")
                else:
                    verified_attempts.append(attempt)
            else:
                verified_attempts.append(attempt + "\n\n[NO BOXED ANSWER FOUND]")

        # STEP 5: ENSEMBLE & SYNTHESIZE
        final_answer = await self.ensemble(
            instruction="""Select or synthesize the best final answer:
            1. Prefer solutions with successful computational verification.
            2. If multiple verified answers agree, select that.
            3. If disagreement, analyze which solution has the most rigorous justification.
            4. Extract the final 3-digit answer in format \\boxed{XXX}.
            5. If no clear winner, choose the most conservative/defensible answer.
            Output ONLY the final answer in format: \\boxed{XXX}""",
            contexts_list=verified_attempts
        )

        # STEP 6: FINAL SANITY CHECK & REVISION LOOP (UP TO 2 ITERATIONS)
        for _ in range(2):
            box_match = re.search(r"\\boxed\{(\d{3})\}", final_answer)
            if not box_match:
                final_answer = await self.revise(
                    instruction="""Final answer is malformed. Extract or compute the 3-digit integer answer.
                    Ensure output is exactly in format: \\boxed{XXX} where XXX is 000-999.
                    If uncertain, recompute from the most reliable solution attempt.""",
                    context=final_answer
                )
            else:
                candidate = box_match.group(1)
                if len(candidate) == 3 and candidate.isdigit():
                    break
                else:
                    final_answer = await self.revise(
                        instruction=f"""Answer {candidate} is invalid. Must be 3-digit integer 000-999.
                        Recompute or extract correct answer. Output ONLY: \\boxed{{XXX}}""",
                        context=final_answer
                    )

        return final_answer