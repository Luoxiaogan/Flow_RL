# Workflow ID: limr_0_0
# Benchmark: limr
# Data Indices: [293, 231]

# --- DO NOT IMPORT HERE ---
class Workflow:
    def __init__(self, config, problem) -> None:
        # --- DO NOT MODIFY THIS SECTION ---
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
        """
        Universal workflow for LIMR mathematical competition problems.
        Dynamically adapts strategy based on problem structure.
        Combines classification, parallel exploration, decomposition, computation, and validation.
        """
        import asyncio
        import re

        # STEP 1: META-ANALYSIS — Classify problem and generate solution strategy profile
        strategy_profile = await self.generate(
            instruction="""Perform deep structural analysis of this mathematical problem:

1. CLASSIFY DOMAIN: Is this primarily algebra, combinatorics, number theory, geometry, calculus, or functional reasoning? 
2. IDENTIFY KEY INSIGHT: What is the non-obvious transformation, theorem, or trick likely required? (e.g., telescoping, modular arithmetic, induction, coordinate transform)
3. ASSESS DECOMPOSABILITY: Can this be broken into clear, ordered subproblems? If yes, list them.
4. COMPUTATIONAL NEED: Does this require heavy computation, symbolic manipulation, or is it insight-only?
5. VALIDATION RISK: What are the most likely error points? (e.g., off-by-one, domain restrictions, undefined inverses)
6. ANSWER FORMAT: What form should the final answer take? (Integer 000-999, or "NEI" if undefined)

Output in this exact JSON-like structure (without actual JSON syntax):
DOMAIN: [domain]
INSIGHT: [key insight]
DECOMPOSABLE: [yes/no]
SUBPROBLEMS: [if yes, list; else "N/A"]
COMPUTATION: [heavy/light/none]
RISKS: [list of risks]
FORMAT: [integer/NEI]""",
            context=""
        )

        # STEP 2: DYNAMIC STRATEGY SELECTION — Choose workflow branch based on strategy profile
        if "DECOMPOSABLE: yes" in strategy_profile:
            # HIERARCHICAL DECOMPOSITION BRANCH
            decomposition = await self.decompose(
                instruction="""Break this problem into minimal, ordered subproblems. Each subproblem should be:
- Self-contained with clear input/output
- Solvable with one primary technique (algebra, computation, etc.)
- Dependencies explicitly stated (which subproblems must be solved first)
- Final subproblem must output the required integer or "NEI"

Output as list of subproblem dicts with 'id', 'description', 'dependencies'.""",
                context=strategy_profile
            )

            # Solve subproblems in topological order
            solved = {}
            for sub in decomposition:
                deps = sub['dependencies'].split(',') if sub['dependencies'] else []
                # Wait for dependencies (simplistic topological sort)
                for dep_id in deps:
                    if dep_id.strip() and dep_id.strip() not in solved:
                        # In real implementation, we'd handle this with proper DAG scheduling
                        # For simplicity, assume decomposition is already topologically sorted
                        pass

                # Solve current subproblem
                if "compute" in sub['description'].lower() or "calculate" in sub['description'].lower():
                    # Use Programmer for computational subproblems
                    sub_solution = await self.programmer(
                        instruction=f"""Solve this subproblem exactly:
{sub['description']}

Use Python. Ensure:
- No floating point approximations unless unavoidable (then round correctly)
- Handle edge cases (division by zero, undefined inverses, etc.)
- Return ONLY the final answer as integer or "NEI"

Context from previous subproblems: {solved}""",
                        context=strategy_profile,
                        max_retries=3
                    )
                else:
                    # Use Generate for conceptual subproblems
                    sub_solution = await self.generate(
                        instruction=f"""Solve this subproblem through mathematical reasoning:
{sub['description']}

Requirements:
- Show key steps but be concise
- Justify non-obvious moves
- Output final result as integer or "NEI"

Context from previous subproblems: {solved}""",
                        context=strategy_profile
                    )

                # Validate and refine sub-solution
                refined = await self.revise(
                    instruction="""Critique this solution as a math competition grader:
1. Check for logical gaps or unjustified assumptions
2. Verify arithmetic and algebraic manipulations
3. Ensure answer format compliance (integer 000-999 or "NEI")
4. If errors found, correct them. If ambiguous, state assumptions.

Output ONLY the corrected final answer (integer or "NEI").""",
                    context=sub_solution
                )
                solved[sub['id']] = refined

            # Final answer is the last subproblem's solution
            final_answer_raw = solved[decomposition[-1]['id']]

        else:
            # PARALLEL EXPLORATION BRANCH — Spawn multiple solution attempts
            approaches = [
                "ALGEBRAIC: Solve through symbolic manipulation, equation solving, and algebraic identities.",
                "COMPUTATIONAL: Direct numerical computation or algorithmic approach.",
                "TRANSFORMATIONAL: Apply non-obvious insight (telescoping, substitution, symmetry, etc.).",
                "BOUNDARY ANALYSIS: Check edge cases, special values, and limiting behavior."
            ]

            # Generate parallel solution attempts
            solution_attempts = await asyncio.gather(
                *[self.generate(
                    instruction=f"""Solve the problem using this approach:
{approach}

Instructions:
- Focus on the core insight of this approach
- Show critical steps but avoid verbosity
- If approach is infeasible, state why and output "NEI"
- Final output must be integer 000-999 or "NEI"

Strategy context: {strategy_profile}""",
                    context=""
                ) for approach in approaches]
            )

            # Refine each attempt
            refined_attempts = await asyncio.gather(
                *[self.revise(
                    instruction="""Improve this solution:
1. Fix any mathematical errors
2. Fill logical gaps
3. Ensure answer is integer 000-999 or "NEI"
4. If solution is invalid, output "NEI"

Output ONLY the final corrected answer.""",
                    context=attempt
                ) for attempt in solution_attempts]
            )

            # Ensemble: Select best or synthesize
            final_answer_raw = await self.ensemble(
                instruction="""Select the most correct and complete answer from these attempts:
- Prefer answers with clear, rigorous justification
- If multiple valid answers, pick the one with simplest derivation
- If all answers are "NEI" or invalid, output "NEI"
- If answers conflict, synthesize by identifying common correct core

Output ONLY the final integer (000-999) or "NEI".""",
                contexts_list=refined_attempts
            )

        # STEP 3: FINAL VALIDATION AND FORMATTING
        final_answer = await self.revise(
            instruction="""Final validation and formatting:
1. Ensure answer is integer between 000 and 999 OR "NEI"
2. If integer, format as 3-digit string with leading zeros (e.g., 5 → "005", 123 → "123")
3. If answer is "NEI", output exactly "NEI"
4. If answer is outside 000-999, check if rounding or modulo is required per problem context

Output ONLY the final formatted answer.""",
            context=final_answer_raw
        )

        # Extract just the answer (remove any explanatory text)
        # Look for 3-digit number or "NEI"
        match = re.search(r'(NEI|\d{3})', final_answer)
        if match:
            return match.group(1)
        else:
            # Fallback: try to extract any integer and format it
            numbers = re.findall(r'\d+', final_answer)
            if numbers:
                num = int(numbers[0]) % 1000  # Clamp to 000-999
                return f"{num:03d}"
            else:
                return "NEI"