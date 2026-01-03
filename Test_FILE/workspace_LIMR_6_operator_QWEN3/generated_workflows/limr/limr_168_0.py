# Workflow ID: limr_168_0
# Benchmark: limr
# Data Indices: [171, 282]

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

        # STEP 1: Generate multi-perspective analyses in parallel (Diamond Fork)
        perspectives = await asyncio.gather(
            self.generate(
                instruction="""Adopt an ALGEBRAIC/ANALYTICAL lens:
                - Identify all variables, expressions, equations, and functional relationships.
                - Look for symmetries, invariants, substitutions, or transformations.
                - Propose a solution path using algebraic manipulation, identities, or calculus.
                - Highlight any potential simplifications or factorizations.
                - If complex numbers, logarithms, or polynomials appear, focus on their properties.
                Output a detailed, step-by-step reasoning draft.""",
                context=""
            ),
            self.generate(
                instruction="""Adopt a GEOMETRIC/COMBINATORIAL lens:
                - If diagram or spatial relations exist, assign coordinates or use vector geometry.
                - Identify combinatorial structures: permutations, combinations, graph structures, counting principles.
                - Look for recursive patterns, generating functions, or probabilistic interpretations.
                - Apply geometric theorems (e.g., angle bisector, similar triangles, coordinate transformations).
                - Propose a solution path grounded in spatial or discrete reasoning.
                Output a detailed, step-by-step reasoning draft.""",
                context=""
            ),
            self.generate(
                instruction="""Adopt a COMPUTATIONAL/NUMERICAL lens:
                - Identify quantities that can be computed directly or via algorithm.
                - Propose writing code to simulate, iterate, or brute-force small cases to detect patterns.
                - Focus on modular arithmetic, prime factorization, or sequence generation if applicable.
                - Suggest numerical approximations ONLY if they can lead to exact integer via pattern recognition.
                - Outline a pseudocode or algorithmic approach.
                Output a detailed, step-by-step reasoning draft.""",
                context=""
            )
        )

        # STEP 2: Refine each perspective for rigor and completeness
        refined_perspectives = await asyncio.gather(
            *[self.revise(
                instruction=f"""Improve this analysis:
                - Fill logical gaps; ensure each step follows from the previous.
                - Add missing justifications or theorems.
                - Correct any algebraic, geometric, or computational errors.
                - Ensure final answer format is an integer 000-999.
                - If stuck, propose an alternative sub-approach within the same lens.""",
                context=p
            ) for p in perspectives]
        )

        # STEP 3: Ensemble synthesize — don't pick one, fuse the best insights
        synthesized = await self.ensemble(
            instruction="""Synthesize a unified solution by integrating insights from all three perspectives:
            - If one perspective yields a closed-form and another a computational verification, combine them.
            - Resolve contradictions by identifying flawed assumptions in weaker arguments.
            - Prioritize solutions that are mathematically elegant AND computationally verifiable.
            - Output must include: 
              1. Final answer as integer between 000 and 999.
              2. Brief justification citing key steps from multiple perspectives.
              3. Confidence level (High/Medium/Low) based on internal consistency.""",
            contexts_list=refined_perspectives
        )

        # STEP 4: Extract problem anatomy for decomposition
        anatomy = await self.generate(
            instruction="""Extract structured problem anatomy:
            - Entities: variables, constants, functions, geometric objects.
            - Constraints: equations, inequalities, domain restrictions, diagram conditions.
            - Goals: what must be computed or proven? What form must the answer take?
            - Hidden clues: symmetries, invariants, or contest-math tricks hinted at.
            Format as JSON-like key-value pairs for consumption by Decompose operator.""",
            context=synthesized
        )

        # STEP 5: Decompose into verifiable subproblems
        subproblems = await self.decompose(
            instruction=f"""Decompose using this anatomy:
            {anatomy}
            
            Guidelines:
            - Each subproblem must be solvable via one core technique (algebra, geometry, code, etc.).
            - Specify dependencies: e.g., "Subproblem 2 needs output of Subproblem 1".
            - Ensure at least one subproblem is amenable to Programmer verification.
            - Avoid vague subproblems like "solve the problem"; be atomic and actionable.
            Return list of subproblems with 'id', 'description', 'dependencies'.""",
            context=anatomy
        )

        # STEP 6: Solve subproblems in dependency order
        solved_subproblems = {}
        # Topological sort by dependencies (simplified for linear dependency chains)
        for sp in subproblems:
            deps = sp.get('dependencies', "").split(",") if sp.get('dependencies') else []
            # Wait for dependencies (in real impl, use proper topological sort)
            await asyncio.sleep(0)  # yield

            # Generate solution attempt for this subproblem
            attempt = await self.generate(
                instruction=f"""Solve this subproblem:
                {sp['description']}
                
                Context from dependencies: {[solved_subproblems.get(d.strip(), 'None') for d in deps if d.strip()]}
                
                - If computational, propose code.
                - If theoretical, derive symbolically.
                - Output must be self-contained and precise.""",
                context="\n".join([f"{d}: {solved_subproblems.get(d.strip(), '')}" for d in deps if d.strip()])
            )

            # If involves computation, verify with Programmer
            if any(kw in sp['description'].lower() for kw in ['compute', 'calculate', 'find value', 'sum', 'product', 'mod', 'prime']):
                code_result = await self.programmer(
                    instruction=f"""Implement and execute code to solve:
                    {sp['description']}
                    
                    Use previous reasoning: {attempt[:500]}...""",
                    context=attempt,
                    max_retries=2
                )
                # Revise attempt with code result
                attempt = await self.revise(
                    instruction=f"""Incorporate computational result:
                    {code_result}
                    
                    Reconcile with theoretical derivation. Fix discrepancies.""",
                    context=attempt
                )

            solved_subproblems[sp['id']] = attempt

        # STEP 7: Re-synthesize with subproblem results
        final_synthesis = await self.ensemble(
            instruction="""Re-synthesize final answer using solved subproblems:
            - Cross-validate subproblem outputs against each other and original synthesis.
            - If contradictions, identify root cause and correct.
            - Final output MUST be a single integer between 000 and 999.
            - Include one-line justification.""",
            contexts_list=[synthesized] + list(solved_subproblems.values())
        )

        # STEP 8: Adversarial validation loop (max 1 iteration)
        for _ in range(1):
            critique = await self.generate(
                instruction="""Critique the current solution:
                - What is the weakest assumption or most likely error?
                - Is there an edge case or constraint overlooked?
                - Could the answer be validated via an independent method?
                - If confidence is not High, propose a fix or alternative approach.""",
                context=final_synthesis
            )
            
            if "high" in critique.lower() and "no error" in critique.lower():
                break  # Confidence is sufficient
            
            # Revise based on critique
            final_synthesis = await self.revise(
                instruction=f"""Address the critique:
                {critique}
                
                Strengthen weak points, fix errors, or switch approach if necessary.
                Maintain integer 000-999 output format.""",
                context=final_synthesis
            )

        # STEP 9: Final validation — ensure answer is integer 000-999
        answer_validation = await self.programmer(
            instruction="""Validate final answer:
            - Extract the integer from the solution.
            - Verify it is between 000 and 999 inclusive.
            - If multiple candidates, select the one consistent with all subproblems.
            - If none, return 000 as fallback (should not happen).
            Output only the 3-digit integer.""",
            context=final_synthesis,
            max_retries=1
        )

        # Extract and return the final answer
        match = re.search(r'\b(\d{3})\b', answer_validation)
        if match:
            return match.group(1)
        else:
            # Fallback: extract any integer and format to 3-digit
            numbers = re.findall(r'\d+', final_synthesis)
            if numbers:
                ans = int(numbers[0]) % 1000
                return f"{ans:03d}"
            else:
                return "000"  # ultimate fallback