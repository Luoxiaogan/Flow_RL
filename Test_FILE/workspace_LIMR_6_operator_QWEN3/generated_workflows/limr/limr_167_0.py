# Workflow ID: limr_167_0
# Benchmark: limr
# Data Indices: [199, 31]

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

        # PHASE 1: META-ANALYSIS & STRATEGY ROUTING
        meta_analysis = await self.generate(
            instruction="""Perform deep problem typing and solution strategy inference:
            1. Classify the mathematical domain (geometry, number theory, combinatorics, algebra, optimization).
            2. Identify key mathematical structures (symmetry, modular arithmetic, recursive sequences, inequalities, etc.).
            3. Infer the solution archetype (cycle detection, extremal optimization, counting with constraints, etc.).
            4. Predict required techniques (coordinate geometry, prime factorization, generating functions, etc.).
            5. Estimate computational complexity and feasibility of brute-force approaches.
            6. Propose 2-3 distinct solution strategies with their risk/reward profiles.
            Output as a structured analysis with clear section headers.""",
            context=""
        )

        # PHASE 2: PARALLEL STRATEGY EXECUTION
        # Track 1: Domain-Specialized Analytical Solution
        domain_strategy = await self.generate(
            instruction=f"""Based on this meta-analysis:
            {meta_analysis}

            Develop a complete analytical solution:
            - Use domain-specific mathematical formalism
            - Show all logical steps with justifications
            - Handle edge cases and boundary conditions
            - Derive the exact integer answer between 000-999
            - If stuck, explicitly state the blocking assumption and propose alternatives""",
            context=meta_analysis
        )

        # Track 2: Structural Decomposition
        decomposition = await self.decompose(
            instruction="""Break this problem into minimal, solvable subproblems:
            - Each subproblem should be independently verifiable
            - Specify dependencies between subproblems
            - Prioritize computational subproblems for programmer operator
            - Include at least one 'verification' subproblem to validate final answer
            Format as list of dictionaries with 'id', 'description', 'dependencies'""",
            context=""
        )

        # Solve decomposition subproblems in dependency order
        solved_subproblems = {}
        for subproblem in sorted(decomposition, key=lambda x: len(x.get('dependencies', '').split(',')) if x.get('dependencies') else 0):
            sub_id = subproblem['id']
            deps = [solved_subproblems[dep_id] for dep_id in subproblem.get('dependencies', '').split(',') if dep_id in solved_subproblems] if subproblem.get('dependencies') else []
            
            context_for_sub = "\n".join(deps) if deps else ""
            solution_attempt = await self.generate(
                instruction=f"""Solve this subproblem:
                {subproblem['description']}
                
                Use previous results if available:
                {context_for_sub}
                
                Be precise and show all work. If computational, consider using programmer operator.""",
                context=context_for_sub
            )
            
            # If subproblem seems computational, try programmer
            if any(kw in solution_attempt.lower() for kw in ['compute', 'calculate', 'iterate', 'loop', 'for ', 'range']):
                try:
                    program_solution = await self.programmer(
                        instruction=f"""Implement a solution for: {subproblem['description']}
                        Use previous context: {context_for_sub}
                        Return only the computed result, no explanations.""",
                        context=solution_attempt,
                        max_retries=2
                    )
                    solution_attempt = f"PROGRAMMER RESULT: {program_solution}\nANALYTICAL ATTEMPT: {solution_attempt}"
                except Exception:
                    pass  # Fall back to analytical solution
            
            solved_subproblems[sub_id] = solution_attempt

        decomposition_solution = "\n\n".join([f"Subproblem {k}: {v}" for k, v in solved_subproblems.items()])

        # Track 3: Computational Brute-Force/Heuristic
        computational_approach = await self.programmer(
            instruction=f"""Based on the problem and meta-analysis:
            {meta_analysis}
            
            Implement a computational solution:
            - Use reasonable bounds and heuristics to limit search space
            - Prioritize efficiency but ensure correctness
            - Return the exact integer answer
            - If multiple solutions, return the one satisfying all constraints
            - Include verification step against problem conditions""",
            context=meta_analysis,
            max_retries=3
        )

        # PHASE 3: SYNTHESIS & VERIFICATION
        candidate_solutions = [
            domain_strategy,
            decomposition_solution,
            f"COMPUTATIONAL APPROACH RESULT: {computational_approach}"
        ]

        # Cross-validate and synthesize
        synthesized = await self.ensemble(
            instruction="""Synthesize these solution attempts:
            1. Compare answers - if all agree, select that answer.
            2. If conflict, identify which method has strongest logical foundation.
            3. For conflicting answers, generate a reconciliation: what assumption caused divergence?
            4. Apply verification: does the answer satisfy all original problem constraints?
            5. Extract the final integer answer between 000-999.
            6. Format as: "FINAL_ANSWER: XXX" where XXX is the 3-digit answer.""",
            contexts_list=candidate_solutions
        )

        # Final revision for precision and format
        final_answer = await self.revise(
            instruction="""Extract and verify the final answer:
            1. Locate the integer answer in the text (should be between 000-999).
            2. If not in 3-digit format, convert it (e.g., 75 becomes 075).
            3. Verify it satisfies all problem constraints.
            4. If no clear answer, re-express the most consistent result as 3-digit.
            5. Output ONLY the 3-digit string, nothing else.""",
            context=synthesized
        )

        # Ensure 3-digit format
        match = re.search(r'\b(\d{1,3})\b', final_answer)
        if match:
            answer = match.group(1).zfill(3)
            if int(answer) > 999:
                answer = "999"
        else:
            # Fallback: extract any number and clamp
            numbers = re.findall(r'\d+', final_answer)
            answer = numbers[0].zfill(3)[:3] if numbers else "000"

        return answer