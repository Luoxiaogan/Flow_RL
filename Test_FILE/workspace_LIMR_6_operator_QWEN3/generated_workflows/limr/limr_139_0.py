# Workflow ID: limr_139_0
# Benchmark: limr
# Data Indices: [5, 269]

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

        # STEP 1: META-COGNITIVE CLASSIFICATION
        classification = await self.generate(
            instruction="""Perform a deep structural analysis of this mathematical problem. Identify:
            1. Primary and secondary mathematical domains (e.g., algebra, geometry, number theory, combinatorics, trigonometry)
            2. Key mathematical objects and operations involved (e.g., polynomials, angles, inequalities, sequences)
            3. Likely solution strategies (symbolic manipulation, computational brute force, geometric insight, induction, etc.)
            4. Estimated complexity (number of non-trivial steps required)
            5. Whether decomposition into subproblems is necessary or beneficial
            6. Potential pitfalls or non-obvious insights required
            7. Expected form of the final answer (must be integer 000-999)
            Format your response as a structured analysis with clear section headers.""",
            context=""
        )

        # STEP 2: STRATEGY BRANCHING BASED ON CLASSIFICATION
        if "decompos" in classification.lower() or "subproblem" in classification.lower() or "multi-step" in classification.lower():
            # HIERARCHICAL DECOMPOSITION PATH
            subproblems = await self.decompose(
                instruction="""Break this problem into minimal, logically independent subproblems. Each subproblem should:
                - Be solvable in isolation (given its dependencies)
                - Have a clear input-output relationship
                - Contribute directly to the final answer
                - Be tagged with required mathematical domain
                Return as list of subproblem dicts with 'id', 'description', 'dependencies'.""",
                context=classification
            )
            
            # SOLVE SUBPROBLEMS IN TOPOLOGICAL ORDER (respecting dependencies)
            solutions = {}
            solved_ids = set()
            
            # Simple topological sort (assuming no cycles)
            while len(solved_ids) < len(subproblems):
                for sp in subproblems:
                    if sp['id'] in solved_ids:
                        continue
                    deps_met = all(dep.strip() in solved_ids for dep in sp['dependencies'].split(',') if dep.strip())
                    if deps_met:
                        # Generate solution attempt
                        sol_attempt = await self.generate(
                            instruction=f"""Solve this subproblem:
                            {sp['description']}
                            
                            Context from problem classification:
                            {classification}
                            
                            Previously solved subproblems:
                            {[f"{sid}: {solutions[sid]}" for sid in solved_ids]}
                            
                            Show all steps. Be precise. Final output must be clearly boxed.""",
                            context=""
                        )
                        # Revise for correctness
                        sol_refined = await self.revise(
                            instruction="""Critically verify this solution:
                            - Check for algebraic/trigonometric/logical errors
                            - Ensure all constraints are satisfied
                            - Confirm intermediate steps are justified
                            - Final answer must be numerical if applicable
                            If error found, correct it and explain the fix.""",
                            context=sol_attempt
                        )
                        solutions[sp['id']] = sol_refined
                        solved_ids.add(sp['id'])
            
            # SYNTHESIZE FINAL ANSWER FROM SUBPROBLEM SOLUTIONS
            synthesis = await self.generate(
                instruction=f"""Combine the following subproblem solutions into a complete, coherent solution to the original problem:
                {[f"Subproblem {sid}: {sol}" for sid, sol in solutions.items()]}
                
                Ensure logical flow from subproblems to final answer. The final answer must be an integer between 000 and 999, clearly boxed at the end.""",
                context=""
            )
            final_answer_raw = synthesis

        else:
            # PARALLEL STRATEGY GENERATION PATH
            strategy_attempts = await asyncio.gather(
                self.generate(
                    instruction=f"""Strategy 1: Algebraic/Analytical Approach
                    Based on classification: {classification}
                    Solve using symbolic manipulation, identities, and analytical reasoning. Show all steps. Derive exact answer.""",
                    context=""
                ),
                self.generate(
                    instruction=f"""Strategy 2: Computational/Algorithmic Approach
                    Based on classification: {classification}
                    Formulate as a computational problem. Write pseudocode or describe algorithm. Consider edge cases and constraints. Compute exact answer.""",
                    context=""
                ),
                self.generate(
                    instruction=f"""Strategy 3: Geometric/Visual or Insight-Based Approach
                    Based on classification: {classification}
                    Look for geometric interpretations, symmetry, or non-obvious transformations. Use diagrams or spatial reasoning if applicable. Derive answer through insight.""",
                    context=""
                )
            )
            
            # REVISE EACH STRATEGY FOR CORRECTNESS
            revised_attempts = await asyncio.gather(
                *[self.revise(
                    instruction="""Critically examine this solution:
                    - Verify mathematical correctness step by step
                    - Check for consistency with original problem constraints
                    - Ensure final answer is an integer between 000 and 999
                    - Fix any errors found and explain corrections""",
                    context=attempt
                ) for attempt in strategy_attempts]
            )
            
            # ENSEMBLE SYNTHESIS
            final_answer_raw = await self.ensemble(
                instruction="""Synthesize the best elements from all solution attempts:
                - Identify consensus answer if all agree
                - If disagreement, trace back to first principles and resolve contradictions
                - Prefer solutions with clear, rigorous derivations
                - Final output must be a single, boxed integer between 000 and 999
                - Include brief justification for chosen answer""",
                contexts_list=revised_attempts
            )

        # FINAL VERIFICATION AND EXTRACTION
        verified_answer = await self.revise(
            instruction="""Final verification step:
            - Extract the final numerical answer (must be integer 000-999)
            - Confirm it satisfies ALL original problem constraints
            - If multiple answers possible, ensure the correct one (smallest, largest, only, etc.) is selected per problem
            - Format as exactly three digits (e.g., 042, not 42)
            - If answer not found or invalid, state 'ERROR'""",
            context=final_answer_raw
        )

        # PROGRAMMATIC EXTRACTION (FALLBACK)
        extraction_code = await self.programmer(
            instruction="""Extract the final three-digit answer from the following text. 
            The answer is an integer between 000 and 999, possibly embedded in text. 
            Use regex or string parsing. Return ONLY the three-digit string (e.g., "042").
            If no valid answer found, return "000" as fallback.""",
            context=verified_answer
        )

        # CLEAN EXTRACTION
        match = re.search(r'\b([0-9]{3})\b', extraction_code)
        if match:
            final_answer = match.group(1)
        else:
            # LAST RESORT: SEARCH IN VERIFIED_ANSWER
            match2 = re.search(r'\b([0-9]{1,3})\b', verified_answer)
            if match2:
                num = int(match2.group(1))
                if 0 <= num <= 999:
                    final_answer = f"{num:03d}"
                else:
                    final_answer = "000"
            else:
                final_answer = "000"

        return final_answer