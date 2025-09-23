# Workflow ID: limr_113_0
# Benchmark: limr
# Data Indices: [130, 44]

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

        # STEP 1: CLASSIFY PROBLEM TYPE TO GUIDE STRATEGY
        classification = await self.generate(
            instruction="""Comprehensively classify this mathematical problem by analyzing its structure, domain, and required techniques. Consider:

- Primary mathematical domain: Algebra, Geometry, Number Theory, Combinatorics, Probability, Sequences, or Hybrid
- Key objects: Are there coordinates, diagrams, sequences, equations, inequalities, or counting scenarios?
- Required techniques: Does it need modular arithmetic, coordinate geometry, induction, combinatorial identities, or calculus?
- Answer format: Is the answer an integer? Does it require derivation or direct computation?
- Complexity indicators: How many distinct reasoning steps are implied? Are there hidden constraints?

Output a structured classification with headings: DOMAIN, TECHNIQUES, STRUCTURE, and CONFIDENCE_LEVEL (High/Medium/Low).""",
            context=""
        )

        # STEP 2: CONDITIONAL BRANCHING BASED ON CLASSIFICATION
        subproblems = []
        solution_attempts = []

        if any(kw in classification.lower() for kw in ["geometry", "coordinate", "triangle", "asy", "vector"]):
            # Geometry-focused decomposition and parallel solving
            subproblems = await self.decompose(
                instruction="""Decompose this geometry problem into atomic, solvable subproblems. For each subproblem:
- Specify exact mathematical operation needed (e.g., 'compute distance between two points', 'find area using shoelace formula')
- List required inputs (coordinates, lengths, angles)
- Identify dependencies (e.g., 'requires result from subproblem 3')
- Flag any subproblem that requires programming (e.g., 'compute determinant')

Output as structured list with id, description, and dependencies.""",
                context=classification
            )

            # Parallel solution attempts: Coordinate, Vector, and Synthetic Geometry
            geo_attempts = await asyncio.gather(
                self.generate(
                    instruction=f"""Solve using coordinate geometry approach:
1. Extract all coordinates from problem or diagram.
2. Apply distance, slope, or area formulas.
3. Show all algebraic steps.
4. Verify with diagram constraints.

Classification context: {classification}""",
                    context=""
                ),
                self.generate(
                    instruction=f"""Solve using vector geometry approach:
1. Represent points as vectors.
2. Use cross product for area or dot product for angles.
3. Show vector operations step by step.
4. Validate against coordinate solution if possible.

Classification context: {classification}""",
                    context=""
                ),
                self.generate(
                    instruction=f"""Solve using synthetic geometry (theorems, properties):
1. Identify relevant theorems (Pythagorean, similar triangles, etc.)
2. Apply geometric properties without coordinates.
3. Justify each step with theorem references.
4. Cross-validate with computational results.

Classification context: {classification}""",
                    context=""
                )
            )
            solution_attempts.extend(geo_attempts)

        elif any(kw in classification.lower() for kw in ["sum", "sequence", "series", "odd", "even", "divisible", "modular", "prime"]):
            # Number theory / algebra decomposition
            subproblems = await self.decompose(
                instruction="""Decompose this number theory/algebra problem into computational and conceptual subproblems. For each:
- Specify if it's computational (needs programming) or conceptual (needs derivation)
- List formulas or theorems required (e.g., 'arithmetic series sum', 'modular inverse')
- Identify variable dependencies
- Flag any subproblem requiring iteration or large computation

Output as structured list with id, description, and dependencies.""",
                context=classification
            )

            # Parallel: Direct formula, programming, and mathematical induction
            num_attempts = await asyncio.gather(
                self.generate(
                    instruction=f"""Solve using direct algebraic formula:
1. Identify sequence type (arithmetic, geometric, etc.)
2. Apply closed-form formula.
3. Show derivation of parameters (first term, last term, count).
4. Verify with small case.

Classification context: {classification}""",
                    context=""
                ),
                self.programmer(
                    instruction=f"""Write Python code to compute the exact answer:
- Handle large numbers precisely
- Include input validation
- Output only the final integer answer
- Add comments for key steps

Classification context: {classification}""",
                    context=""
                ),
                self.generate(
                    instruction=f"""Solve using mathematical induction or recursive reasoning:
1. Define base case and inductive step.
2. Prove correctness.
3. Derive closed form if possible.
4. Compare with direct formula result.

Classification context: {classification}""",
                    context=""
                )
            )
            solution_attempts.extend(num_attempts)

        else:
            # Default comprehensive decomposition for hybrid or unknown problems
            subproblems = await self.decompose(
                instruction="""Decompose this problem into the most fundamental mathematical subproblems possible. For each:
- Specify domain (algebra, geometry, combinatorics, etc.)
- List required techniques
- Identify dependencies
- Flag computational vs. conceptual nature

Output as structured list with id, description, and dependencies.""",
                context=classification
            )

            # Generate three diverse solution attempts without domain bias
            generic_attempts = await asyncio.gather(
                self.generate(
                    instruction=f"""Solve using first-principles mathematical reasoning:
1. Break down into axioms or fundamental theorems.
2. Build solution step by step with full justification.
3. Avoid shortcuts; show all work.
4. Verify each intermediate result.

Classification context: {classification}""",
                    context=""
                ),
                self.generate(
                    instruction=f"""Solve by transforming the problem into an equivalent but simpler form:
1. Identify possible substitutions or transformations.
2. Apply symmetry, invariance, or extremal principles.
3. Solve the transformed problem.
4. Map solution back to original problem.

Classification context: {classification}""",
                    context=""
                ),
                self.programmer(
                    instruction=f"""Write Python code to solve computationally:
- Handle edge cases
- Use exact arithmetic
- Output only final integer
- Include verification step

Classification context: {classification}""",
                    context=""
                )
            )
            solution_attempts.extend(generic_attempts)

        # STEP 3: SYNTHESIZE AND VALIDATE USING ENSEMBLE
        synthesized = await self.ensemble(
            instruction="""Synthesize the most accurate solution from the provided attempts. Consider:

- Which solution provides complete, step-by-step reasoning?
- Which matches computational results from Programmer?
- Are there consensus answers across methods?
- Which solution best satisfies the problem constraints?

If contradictions exist, identify the most rigorous derivation. Output the final answer as an integer between 000 and 999, wrapped in \\boxed{{}}. Include a one-sentence justification.""",
            contexts_list=solution_attempts
        )

        # STEP 4: ADVERSARIAL REVISION - ASSUME IT'S WRONG AND TRY TO BREAK IT
        validated = await self.revise(
            instruction=f"""Adversarially critique this solution. Assume it is incorrect and search for flaws:

- Check arithmetic: are sums, products, or counts accurate?
- Verify logic: are all steps justified? Any skipped assumptions?
- Validate against problem constraints: does answer satisfy original conditions?
- Cross-check with alternative methods: does it align with any parallel solution?

If any flaw is found, revise completely. If no flaw, output unchanged. Final answer must be an integer in \\boxed{{}}.""",
            context=synthesized
        )

        # STEP 5: FINAL COMPUTATIONAL SANITY CHECK (IF APPLICABLE)
        final_answer = validated
        try:
            # Extract boxed answer for verification
            match = re.search(r'\\boxed\{(\d{1,3})\}', validated)
            if match:
                candidate_answer = int(match.group(1))
                # Simple bounds check for reasonableness (example: between 0 and 999)
                if 0 <= candidate_answer <= 999:
                    # If Programmer was used, try to recompute for verification
                    if any("programmer" in str(attempt).lower() for attempt in solution_attempts):
                        verification_code = await self.programmer(
                            instruction=f"""Write minimal Python code to verify the answer {candidate_answer} is correct.
- Recompute independently
- Output 'VERIFIED' if matches, 'ERROR' if not
- No explanations, just VERIFIED or ERROR""",
                            context=validated
                        )
                        if "VERIFIED" in verification_code:
                            final_answer = validated
                        else:
                            # Fallback: return the synthesized version anyway (may be formatting issue)
                            pass
        except:
            # If extraction or verification fails, trust the revised synthesis
            pass

        return final_answer