# Workflow ID: limr_1_0
# Benchmark: limr
# Data Indices: [322, 152]

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

        # STEP 1: CLASSIFY THE PROBLEM AND PLAN STRATEGIES
        classification = await self.generate(
            instruction="""Perform a deep structural analysis of this mathematical problem. Your output must include:

1. Problem Domain Classification: Is this primarily algebra, number theory, combinatorics, geometry, or optimization? Justify briefly.
2. Key Mathematical Objects: Identify polynomials, exponents, sequences, geometric figures, or other core elements.
3. Required Techniques: List applicable methods (e.g., factoring, modular arithmetic, induction, coordinate geometry, generating functions).
4. Potential Solution Pathways: Propose 2-3 distinct high-level strategies. For each, outline the first 2-3 steps.
5. Known Pitfalls: What common mistakes or traps should be avoided? (e.g., sign errors, domain restrictions, overcounting)
6. Expected Answer Format: Confirm that the answer must be an integer 000-999.

Structure your response with clear section headers. Be precise and exhaustive.""",
            context=""
        )

        # STEP 2: PARALLEL SOLUTION ATTEMPTS (DIAMOND PATTERN)
        # Each attempt uses a different strategy inferred from classification
        strategy_1 = await self.generate(
            instruction=f"""Based on the classification:
{classification}

Attempt Solution Strategy 1: Algebraic Manipulation & Symbolic Transformation
- Apply polynomial identities, substitutions, or symmetry exploitation.
- For expressions with high exponents, look for patterns or reductions (e.g., let y = x^4).
- Maintain exact arithmetic; no approximations.
- Show all steps clearly. Verify that final answer is integer 000-999.
- If stuck, note where and why.""",
            context=classification
        )

        strategy_2 = await self.generate(
            instruction=f"""Based on the classification:
{classification}

Attempt Solution Strategy 2: Structural Factorization or Decomposition
- Assume a factored form (e.g., quadratic in x^4) and solve for coefficients.
- Enforce constraints: monic polynomials, integer coefficients.
- Use Vieta’s formulas or coefficient matching if applicable.
- Track variable substitutions and verify reversibility.
- Show all steps. Confirm final answer is integer 000-999.""",
            context=classification
        )

        strategy_3 = await self.programmer(
            instruction=f"""Based on the classification:
{classification}

Write Python code to solve this problem symbolically or numerically.
- Use SymPy for symbolic manipulation if applicable.
- If numerical, ensure exact integer arithmetic (use int, not float).
- Verify constraints (e.g., monic, integer coefficients).
- Print the final answer as an integer between 000 and 999.
- Include comments explaining key steps.
- If symbolic solution fails, try numerical verification at specific points (e.g., x=1).""",
            context=classification,
            max_retries=3
        )

        # STEP 3: ENSEMBLE - SYNTHESIZE BEST SOLUTION
        candidate_solutions = [strategy_1, strategy_2, strategy_3]
        synthesized = await self.ensemble(
            instruction="""You are given three solution attempts for a high-level math problem. Your task:

1. Compare all three for mathematical correctness, completeness, and adherence to constraints.
2. Prioritize solutions that:
   - Provide step-by-step reasoning
   - Satisfy all problem conditions (e.g., monic, integer coefficients)
   - Arrive at an integer answer 000-999
   - Avoid unjustified assumptions
3. If two or more agree on the final answer, select the most clearly reasoned.
4. If they conflict, identify the source of discrepancy and select the most rigorous.
5. Output the chosen solution in full, with a final line: "FINAL ANSWER: XXX" where XXX is the integer.

Do NOT average or blend solutions—select or clearly synthesize.""",
            contexts_list=candidate_solutions
        )

        # STEP 4: REVISE & VERIFY (CASCADE WITH FEEDBACK)
        refined = synthesized
        for _ in range(2):  # Allow up to 2 revision passes
            audit = await self.revise(
                instruction="""Critically audit this solution:

- Check every algebraic step for sign errors, arithmetic mistakes, or invalid operations.
- Verify that all constraints from the original problem are satisfied.
- Ensure the final answer is an integer between 000 and 999.
- If any flaw is found, correct it and re-verify all subsequent steps.
- If no flaws, return the solution unchanged with "VERIFIED" at the end.

Be ruthless. Mathematical rigor is non-negotiable.""",
                context=refined
            )
            if "VERIFIED" in audit:
                refined = audit
                break
            refined = audit  # Update for next iteration

        # STEP 5: FALLBACK DECOMPOSITION (IF STILL UNCERTAIN)
        if "assume" in refined.lower() or "likely" in refined.lower() or "probably" in refined.lower():
            decomposition = await self.decompose(
                instruction="""Break this problem into minimal, independent subproblems:

- Each subproblem should be solvable in isolation.
- Specify dependencies (which subproblems must be solved first).
- For each, state the required technique and expected output format.
- Ensure collectively they determine the final integer answer 000-999.

Return as structured list of dicts with 'id', 'description', 'dependencies'.""",
                context=refined
            )

            # Solve each subproblem recursively (simplified here as sequential for brevity)
            sub_solutions = {}
            for sub in decomposition:
                sub_id = sub['id']
                sub_desc = sub['description']
                deps = sub.get('dependencies', "").split(',') if sub.get('dependencies') else []
                
                # Wait for dependencies (simplified: assume ordered)
                dep_context = "\n".join([sub_solutions.get(d.strip(), "") for d in deps if d.strip() in sub_solutions])
                
                sub_solution = await self.generate(
                    instruction=f"""Solve this subproblem:
{sub_desc}

Context from dependencies:
{dep_context}

Show all steps. Final output must contribute to an integer 000-999 answer.
Return only the subproblem solution, clearly labeled.""",
                    context=dep_context
                )
                sub_solutions[sub_id] = sub_solution

            # Reassemble
            reassembly = await self.generate(
                instruction=f"""Reassemble the full solution from these subproblem solutions:
{json.dumps(sub_solutions, indent=2)}

- Combine logically to derive the final answer.
- Verify consistency and constraints.
- Output final answer as integer 000-999 in format: "FINAL ANSWER: XXX".""",
                context=str(sub_solutions)
            )
            refined = reassembly

        # STEP 6: EXTRACT AND FORMAT FINAL ANSWER
        final_answer = await self.summarize(
            instruction="""Extract the final numerical answer from this solution:

- It MUST be an integer between 000 and 999.
- Remove all explanations, units, or formatting.
- If multiple numbers appear, select the one explicitly stated as the answer.
- If no clear answer, return "000" as fallback.
- Return ONLY the three-digit number, zero-padded (e.g., "042", "123", "007").""",
            context=refined
        )

        # Ensure it's exactly 3 digits
        match = re.search(r'\b(\d{1,3})\b', final_answer)
        if match:
            num = int(match.group(1))
            if 0 <= num <= 999:
                return f"{num:03d}"
        
        # Fallback if extraction fails
        return "000"