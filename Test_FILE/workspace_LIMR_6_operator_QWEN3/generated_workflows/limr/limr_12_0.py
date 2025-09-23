# Workflow ID: limr_12_0
# Benchmark: limr
# Data Indices: [133, 176]

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

        # STEP 1: CLASSIFY PROBLEM DOMAIN AND COMPLEXITY
        classification = await self.generate(
            instruction="""Comprehensively classify this mathematical problem:
            1. Primary domain: Is it combinatorics, number theory, algebra, geometry, optimization, or sequences?
            2. Secondary characteristics: Does it involve counting, modular arithmetic, polynomials, spatial reasoning, maxima/minima, recursion?
            3. Structural complexity: How many distinct reasoning steps are required? Are there hidden symmetries or invariants?
            4. Solution paradigms: What standard techniques apply? (e.g., inclusion-exclusion, generating functions, coordinate geometry, induction)
            5. Potential pitfalls: What are common mistakes or subtle constraints?
            6. Expected answer format: Integer 000-999 — is it a count, a remainder, a coefficient, a length?
            Output as a structured analysis with clear section headers.""",
            context=""
        )

        # STEP 2: GENERATE PARALLEL SOLUTION APPROACHES
        approach_instructions = [
            """Adopt a DIRECT COMPUTATIONAL approach:
            - Translate the problem into explicit mathematical operations
            - Identify all variables and constraints
            - Derive equations or counting formulas step by step
            - Prioritize precision and completeness over elegance
            - Show all intermediate calculations""",
            
            """Adopt a STRUCTURAL INSIGHT approach:
            - Look for symmetries, invariants, or transformations
            - Can the problem be reduced to a known theorem or identity?
            - Are there clever substitutions or re-framings that simplify it?
            - Focus on 'aha' moments rather than brute force
            - Justify non-obvious steps rigorously""",
            
            """Adopt a LATERAL SHORTCUT approach:
            - Ignore apparent complexity — search for hidden patterns
            - Could modular arithmetic, parity, or bounding avoid heavy computation?
            - Is there a probabilistic or combinatorial identity that applies?
            - Test small cases to guess the general form
            - Prioritize elegance and minimalism"""
        ]

        # Generate parallel approaches
        approaches = await asyncio.gather(
            *[self.generate(instruction=instr, context=classification) for instr in approach_instructions]
        )

        # STEP 3: DECOMPOSE EACH APPROACH INTO SUBPROBLEMS (if needed)
        decomposed_solutions = []
        for i, approach in enumerate(approaches):
            # Check if decomposition is warranted (complex problems)
            complexity_check = await self.generate(
                instruction=f"""Based on this approach, estimate its step complexity:
                - Does it require more than 3 distinct logical or computational steps?
                - Are there interdependent subproblems?
                - Would decomposition improve clarity or correctness?
                Answer YES or NO with brief justification.""",
                context=approach
            )
            
            if "YES" in complexity_check.upper():
                # Decompose into subproblems
                subproblems = await self.decompose(
                    instruction="""Break this solution approach into minimal, independent subproblems.
                    For each subproblem:
                    - Define precisely what needs to be computed or proven
                    - Specify any dependencies on other subproblems
                    - Indicate if it requires code execution or pure reasoning
                    Prioritize atomic, verifiable steps.""",
                    context=approach
                )
                
                # Solve subproblems in dependency order (simplified topological sort)
                solved_subproblems = {}
                for sp in subproblems:
                    # Wait for dependencies (simplified: assume linear order)
                    deps = sp.get('dependencies', '').split(',') if sp.get('dependencies') else []
                    for dep_id in deps:
                        dep_id = dep_id.strip()
                        if dep_id and dep_id not in solved_subproblems:
                            # In real implementation, wait for dependency resolution
                            pass
                    
                    # Solve subproblem
                    if "compute" in sp['description'].lower() or "calculate" in sp['description'].lower():
                        solution = await self.programmer(
                            instruction=f"""Solve this subproblem with code:
                            {sp['description']}
                            Ensure precision, handle edge cases, and validate output.""",
                            context=approach
                        )
                    else:
                        solution = await self.generate(
                            instruction=f"""Solve this subproblem through reasoning:
                            {sp['description']}
                            Be rigorous, show all steps, and justify conclusions.""",
                            context=approach
                        )
                        # Revise for rigor
                        solution = await self.revise(
                            instruction="""Critically review this solution:
                            - Are all assumptions justified?
                            - Are there gaps in logic?
                            - Is the conclusion watertight?
                            - Recompute any critical values.
                            Improve clarity and completeness.""",
                            context=solution
                        )
                    solved_subproblems[sp['id']] = solution
                
                # Reconstruct full solution from subproblems
                reconstruction = await self.generate(
                    instruction="""Synthesize all solved subproblems into a complete solution.
                    Maintain logical flow, reference subproblem results, and ensure consistency.
                    The final answer must be an integer between 000 and 999.""",
                    context="\n\n".join([f"Subproblem {k}: {v}" for k, v in solved_subproblems.items()])
                )
                decomposed_solutions.append(reconstruction)
            else:
                # Simple approach — solve directly
                direct_solution = await self.generate(
                    instruction="""Complete this solution approach fully.
                    Show all steps, justify key insights, and compute the final answer.
                    Ensure the answer is an integer 000-999.""",
                    context=approach
                )
                # Revise for rigor
                direct_solution = await self.revise(
                    instruction="""Verify and improve this solution:
                    - Check calculations for arithmetic errors
                    - Ensure no cases are overlooked
                    - Confirm answer format (integer 000-999)
                    - Strengthen any weak reasoning
                    Output a polished, complete solution.""",
                    context=direct_solution
                )
                decomposed_solutions.append(direct_solution)

        # STEP 4: ENSEMBLE AND SYNTHESIZE
        final_answer = await self.ensemble(
            instruction="""Synthesize the best elements from all solution approaches:
            - Cross-validate numerical results — do they agree?
            - Merge correct reasoning fragments into a unified solution
            - Resolve contradictions by prioritizing mathematically rigorous paths
            - If answers differ, identify which approach has the fewest assumptions or highest confidence
            - Output a single, definitive solution with the final answer clearly boxed as a 3-digit integer (000-999).
            Include a confidence assessment (High/Medium/Low) based on consensus and internal consistency.""",
            contexts_list=decomposed_solutions
        )

        # STEP 5: EXTRACT AND FORMAT FINAL ANSWER
        formatted_answer = await self.generate(
            instruction="""Extract the final numerical answer from the solution:
            - It must be an integer between 000 and 999
            - If multiple numbers appear, select the one that answers the original question
            - Format it as exactly three digits, zero-padded (e.g., 42 → 042, 7 → 007)
            - If no valid answer is found, output '000' and flag an error
            Output ONLY the three-digit string, nothing else.""",
            context=final_answer
        )

        # Final revision for format and range compliance
        formatted_answer = await self.revise(
            instruction="""Validate the answer format:
            - Is it exactly three digits?
            - Is it between 000 and 999?
            - Does it match the solution's final conclusion?
            If not, correct it. Output ONLY the three-digit string.""",
            context=formatted_answer
        )

        # Clean output (extract first 3-digit number)
        match = re.search(r'\b\d{3}\b', formatted_answer)
        if match:
            return match.group(0)
        else:
            # Fallback
            return "000"