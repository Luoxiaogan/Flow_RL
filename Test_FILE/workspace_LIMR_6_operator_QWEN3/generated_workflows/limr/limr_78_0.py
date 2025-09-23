# Workflow ID: limr_78_0
# Benchmark: limr
# Data Indices: [118, 300]

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

        # === PHASE 1: PARALLEL HYPOTHESIS GENERATION ===
        hypothesis_instructions = [
            """Analyze the problem through an ALGEBRAIC lens. Focus on:
            - Polynomial identities, functional equations, or algebraic manipulations
            - Variable substitutions or symmetry exploitation
            - Exact symbolic transformations that simplify the problem
            - Potential application of theorems (e.g., Remainder Theorem, Vieta's)
            Output a complete solution path, not just hints.""",
            
            """Analyze the problem through a COMBINATORIAL/PROBABILISTIC lens. Focus on:
            - Counting principles, permutations, combinations, or probability spaces
            - Grouping, partitioning, or recursive structures
            - Symmetry reduction or equivalence class identification
            - Generating functions or recurrence relations if applicable
            Output a complete solution path, not just hints.""",
            
            """Analyze the problem through a NUMBER THEORETIC/GEOMETRIC lens. Focus on:
            - Modular arithmetic, divisibility, or prime factorization
            - Geometric interpretations, coordinate systems, or vector spaces
            - Invariants, extremal principles, or optimization constraints
            - Diophantine equations or lattice point considerations
            Output a complete solution path, not just hints."""
        ]

        hypotheses = await asyncio.gather(
            *[self.generate(instruction=instr, context="") for instr in hypothesis_instructions]
        )

        # === PHASE 2: ADVERSARIAL VALIDATION & REFINEMENT ===
        validated_hypotheses = []
        for i, hyp in enumerate(hypotheses):
            # Spawn a critic for each hypothesis
            critique = await self.generate(
                instruction=f"""Critically evaluate this solution hypothesis:
                - Identify logical gaps, unjustified assumptions, or calculation errors
                - Check boundary conditions and edge cases
                - Assess computational feasibility and precision requirements
                - Suggest specific improvements or alternative approaches
                Be brutally honest and mathematically rigorous.""",
                context=hyp
            )
            
            # Revise hypothesis based on critique
            refined = await self.revise(
                instruction="""Incorporate the critique to produce a corrected, rigorous solution.
                - Fix all identified errors
                - Add missing justifications
                - Clarify ambiguous steps
                - Ensure all claims are mathematically watertight
                Output the complete revised solution.""",
                context=f"Original Hypothesis:\n{hyp}\n\nCritique:\n{critique}"
            )
            validated_hypotheses.append(refined)

        # === PHASE 3: HIERARCHICAL DECOMPOSITION & RECURSIVE SOLVING ===
        # Decompose the most promising hypothesis (we'll pick the most detailed one)
        complexity_scores = [len(h) for h in validated_hypotheses]  # Proxy for depth
        primary_hypothesis = validated_hypotheses[complexity_scores.index(max(complexity_scores))]

        decomposition = await self.decompose(
            instruction="""Break this solution into atomic, solvable subproblems.
            - Each subproblem should be independently verifiable
            - Specify dependencies clearly (which subproblems must be solved first)
            - Include computational or proof requirements for each
            - Aim for 3-7 subproblems maximum""",
            context=primary_hypothesis
        )

        # Solve subproblems recursively (simplified here as linear for brevity, but can be parallelized)
        subproblem_solutions = {}
        for sub in decomposition:
            sub_id = sub['id']
            deps = sub['dependencies'].split(',') if sub['dependencies'] else []
            
            # Wait for dependencies (simplified sequential execution)
            dep_context = "\n".join([f"Subproblem {d}: {subproblem_solutions.get(d, 'UNSOLVED')}" for d in deps if d in subproblem_solutions])
            
            # Generate solution for this subproblem
            sub_solution = await self.generate(
                instruction=f"""Solve this subproblem:
                {sub['description']}
                
                Context from dependencies:
                {dep_context}
                
                Requirements:
                - Show all steps
                - Justify non-trivial claims
                - Output final answer for this subproblem clearly""",
                context=primary_hypothesis
            )
            
            # Validate subproblem solution
            validation = await self.generate(
                instruction="""Verify this subproblem solution:
                - Check internal consistency
                - Validate against dependency constraints
                - Ensure numerical precision and integer output if required
                - Flag any uncertainties or potential errors""",
                context=sub_solution
            )
            
            if "error" in validation.lower() or "uncertain" in validation.lower():
                # Revise if validation fails
                sub_solution = await self.revise(
                    instruction=f"""Fix issues identified in validation:
                    {validation}
                    
                    Ensure solution is mathematically rigorous and complete.""",
                    context=sub_solution
                )
            
            subproblem_solutions[sub_id] = sub_solution

        # === PHASE 4: SYNTHESIZE & COMPUTE ===
        # Reconstruct full solution from subproblems
        full_solution_draft = await self.generate(
            instruction="""Synthesize all subproblem solutions into a complete, coherent solution.
            - Integrate results logically
            - Ensure global consistency
            - Highlight the final answer prominently
            - Format for clarity and mathematical rigor""",
            context=json.dumps(subproblem_solutions, indent=2)
        )

        # Extract computational core for programmer
        computation_strategy = await self.generate(
            instruction="""Extract the precise computational task from this solution.
            - Identify the exact formula, algorithm, or calculation needed
            - Specify input parameters and expected output format
            - Include any precision or integer constraints
            - If symbolic computation is needed, specify the algebraic manipulation
            Output a clear, executable specification for the programmer.""",
            context=full_solution_draft
        )

        # Execute computation
        computed_result = await self.programmer(
            instruction=f"""Execute this mathematical computation:
            {computation_strategy}
            
            Requirements:
            - Use exact arithmetic (no floating point approximations)
            - Output must be an integer between 0 and 999
            - Show all steps if symbolic, or code if algorithmic
            - Verify result against original problem constraints""",
            context=full_solution_draft,
            max_retries=3
        )

        # === PHASE 5: FINAL VALIDATION & ENSEMBLE ===
        final_candidates = [computed_result]
        
        # Cross-validate with alternative hypotheses
        for alt_hyp in validated_hypotheses:
            if alt_hyp != primary_hypothesis:
                alt_computation = await self.generate(
                    instruction="""Extract and compute the final answer from this alternative solution.
                    - Focus only on the numerical result
                    - Apply same precision and integer constraints
                    - If computation is needed, describe it clearly""",
                    context=alt_hyp
                )
                final_candidates.append(alt_computation)

        # Ensemble final answer
        final_answer = await self.ensemble(
            instruction="""Select or synthesize the correct final answer:
            - All candidates must be integers between 0 and 999
            - Prefer answers with complete, verifiable computational paths
            - If candidates conflict, identify the most mathematically rigorous
            - Output ONLY the final integer answer, no explanations""",
            contexts_list=final_candidates
        )

        return final_answer