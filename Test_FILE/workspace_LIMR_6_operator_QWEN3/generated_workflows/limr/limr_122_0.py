# Workflow ID: limr_122_0
# Benchmark: limr
# Data Indices: [183, 298]

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

        # PHASE 1: PARALLEL RECONNAISSANCE - Explore 3 fundamental perspectives
        algebraic_analysis = self.generate(
            instruction="""Adopt a pure algebraic lens. Ignore context and meaning. Focus on:
            - Symbolic manipulation opportunities
            - Polynomial or functional equations hidden in the problem
            - Substitutions that simplify expressions
            - Symmetries in variables or indices
            - Potential factorizations or telescoping
            Output a concrete first step or transformation, not general advice.""",
            context=""
        )
        
        combinatorial_analysis = self.generate(
            instruction="""Adopt a combinatorial/probabilistic lens. Ask:
            - Can this be interpreted as counting arrangements, paths, or states?
            - Are there symmetries or invariants I can exploit?
            - Can I model this as a recurrence or generating function?
            - Is there a probabilistic interpretation or expected value angle?
            Output a concrete counting strategy or combinatorial identity to apply.""",
            context=""
        )
        
        structural_analysis = self.generate(
            instruction="""Adopt a structural/abstract lens. Consider:
            - Group theory, field theory, or linear algebra structures
            - Geometric interpretations or coordinate transformations
            - Graph-theoretic models or network flows
            - Invariants under transformation
            - Connections to known theorems or contest math tricks
            Output a structural insight or non-obvious transformation.""",
            context=""
        )

        # Execute parallel analyses
        perspectives = await asyncio.gather(
            algebraic_analysis, 
            combinatorial_analysis, 
            structural_analysis
        )

        # PHASE 2: SYNTHESIZE INTO GUIDED DECOMPOSITION
        synthesis = await self.ensemble(
            instruction="""You are a master problem-solver synthesizing three perspectives.
            1. Identify the most promising approach (algebraic, combinatorial, structural) based on rigor and tractability.
            2. Extract 1-2 key insights from the other perspectives that can support the main approach.
            3. Formulate a decomposition strategy that leverages the main approach while incorporating supporting insights.
            Output a detailed plan for decomposition.""",
            contexts_list=perspectives
        )

        # Decompose with synthesized strategy
        subproblems = await self.decompose(
            instruction=f"""Decompose the problem using this strategy:
            {synthesis}
            
            Requirements:
            - List subproblems in topological order (no circular dependencies)
            - For each subproblem, specify: 
              a) Type: [symbolic, computational, combinatorial, proof]
              b) Key insight needed
              c) Expected output format
            - Ensure final subproblem yields an integer 000-999
            - Maximum 7 subproblems""",
            context=""
        )

        # PHASE 3: SOLVE SUBPROBLEMS WITH ADAPTIVE EXECUTION
        solutions = {}
        for subproblem in subproblems:
            sub_id = subproblem['id']
            deps = subproblem.get('dependencies', '').split(',') if subproblem.get('dependencies') else []
            
            # Wait for dependencies
            if deps and deps[0]:  # if not empty
                await asyncio.gather(*[solutions.get(dep) for dep in deps if dep in solutions])
            
            # Craft context from dependencies
            dep_context = "\n".join([f"Subproblem {dep}: {solutions[dep]}" for dep in deps if dep in solutions])
            
            # Route based on type
            sub_desc = subproblem['description']
            if "computational" in sub_desc.lower() or "calculate" in sub_desc.lower():
                solution_task = self.programmer(
                    instruction=f"""Solve this computational subproblem:
                    {sub_desc}
                    
                    Constraints:
                    - Use exact arithmetic (no floats)
                    - If combinatorial, use math.comb or itertools sparingly
                    - Max retries: 3
                    - Output only the final number""",
                    context=dep_context,
                    max_retries=3
                )
            else:
                solution_task = self.generate(
                    instruction=f"""Solve this subproblem through reasoning:
                    {sub_desc}
                    
                    Guidelines:
                    - Show key steps but be concise
                    - If proof required, state assumptions clearly
                    - Cross-validate with insights from: {synthesis[:200]}...
                    - Final output must be unambiguous""",
                    context=dep_context
                )
            
            solutions[sub_id] = await solution_task

        # PHASE 4: INTEGRATE AND REVISE
        full_solution = "\n\n".join([f"Step {sp['id']}: {solutions[sp['id']]}" for sp in subproblems])
        
        # Check for uncertainty markers
        needs_refinement = any(phrase in full_solution.lower() 
                             for phrase in ["assume", "likely", "probably", "approximate", "guess"])
        
        if needs_refinement:
            full_solution = await self.revise(
                instruction="""Strengthen this solution:
                1. Eliminate all assumptions—prove or compute exactly
                2. Verify each step against original problem constraints
                3. Add modular arithmetic or bounding arguments where appropriate
                4. Ensure final answer is an integer 000-999 with no decimal points
                5. If stuck, consider contest math tricks: roots of unity, generating functions, or combinatorial identities""",
                context=full_solution
            )

        # PHASE 5: DISTILL AND VALIDATE FINAL ANSWER
        final_answer = await self.summarize(
            instruction="""Extract the final answer with extreme care:
            1. Locate the integer answer between 000 and 999
            2. Verify it appears in at least two independent derivations
            3. Confirm no calculation errors by re-computing key steps symbolically
            4. If answer is not an integer in range, return 'ERROR: NO VALID ANSWER'
            5. Output ONLY the 3-digit integer, zero-padded if necessary""",
            context=full_solution
        )

        # Meta-validation: confidence check
        confidence = await self.generate(
            instruction="""Rate confidence in this answer 1-10:
            10: Multiple independent derivations, all steps verified
            7: One solid derivation with cross-checks
            5: Plausible but unverified assumptions
            3: Guesswork or single fragile path
            1: Contradictions or computational errors
            
            Also identify the weakest step and how to strengthen it.
            Format: 'CONFIDENCE: X/10 | WEAK STEP: [description] | FIX: [action]'""",
            context=f"Solution: {full_solution}\n\nAnswer: {final_answer}"
        )

        # If low confidence, trigger lateral thinking fallback
        if "CONFIDENCE: 1" in confidence or "CONFIDENCE: 3" in confidence:
            lateral_solution = await self.generate(
                instruction=f"""Apply lateral thinking to rescue this problem:
                Original problem: {self.problem_text[:300]}...
                Current answer: {final_answer}
                Weakness: {confidence}
                
                Consider:
                - Physical analogies (e.g., center of mass, random walks)
                - Generating functions or exponential families
                - Roots of unity filter or discrete Fourier transform
                - Probabilistic method or expected value tricks
                - Known contest math identities (e.g., hockey-stick, Catalan)
                Output a new derivation leading to an integer 000-999.""",
                context=""
            )
            
            # Ensemble between original and lateral
            final_answer = await self.ensemble(
                instruction="""Choose the most rigorous answer:
                - Prefer exact derivations over heuristics
                - Prefer answers with multiple verification paths
                - If both flawed, synthesize a hybrid solution
                Output ONLY the 3-digit integer""",
                contexts_list=[final_answer, lateral_solution]
            )

        # Ensure 3-digit format
        match = re.search(r'\b(\d{1,3})\b', final_answer)
        if match:
            num = int(match.group(1))
            if 0 <= num <= 999:
                return f"{num:03d}"
        
        return "000"  # Fallback