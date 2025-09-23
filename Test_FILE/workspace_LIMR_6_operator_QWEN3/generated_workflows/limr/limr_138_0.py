# Workflow ID: limr_138_0
# Benchmark: limr
# Data Indices: [7, 70]

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

        # STEP 1: MULTI-AXIS CLASSIFICATION
        classification = await self.generate(
            instruction="""Perform a deep structural classification of this problem:
            1. Primary Domain: Is this fundamentally algebra, number theory, combinatorics, geometry, or analysis?
            2. Secondary Domains: What other domains are involved? (e.g., a geometry problem using algebra)
            3. Solution Strategy: Does this require construction, proof, optimization, enumeration, or transformation?
            4. Key Constraints: What explicit/implicit constraints govern the solution space?
            5. Answer Format: What form must the answer take? (Integer? Set? Expression?)
            6. Difficulty Indicators: What makes this problem non-trivial? (e.g., hidden symmetries, deceptive simplicity)
            Output as a structured JSON with keys: primary_domain, secondary_domains, strategy, constraints, answer_format, difficulty_indicators.""",
            context=""
        )

        # STEP 2: PARALLEL HYPOTHESIS GENERATION
        algebraic_approach = await self.generate(
            instruction=f"""Assuming this is primarily an ALGEBRAIC problem (even if classification suggests otherwise), develop a complete solution:
            - Translate all conditions into equations/inequalities
            - Identify variables and their domains
            - Apply algebraic manipulations (factoring, substitution, symmetry exploitation)
            - Derive the answer through symbolic reasoning
            - Verify internal consistency
            Classification context: {classification}""",
            context=""
        )

        number_theoretic_approach = await self.generate(
            instruction=f"""Assuming this is primarily a NUMBER THEORY/COMBINATORICS problem, develop a complete solution:
            - Identify discrete structures, modular constraints, or counting principles
            - Apply divisibility rules, prime factorizations, or combinatorial identities
            - Enumerate cases if bounded, or find invariants if unbounded
            - Derive the answer through discrete reasoning
            - Verify against edge cases
            Classification context: {classification}""",
            context=""
        )

        geometric_analytic_approach = await self.generate(
            instruction=f"""Assuming this is primarily a GEOMETRIC/ANALYTIC problem, develop a complete solution:
            - Embed in coordinate system if abstract
            - Apply vector, trigonometric, or calculus-based reasoning
            - Exploit symmetries, invariants, or extremal principles
            - Derive the answer through spatial or continuous reasoning
            - Verify dimensional consistency
            Classification context: {classification}""",
            context=""
        )

        # STEP 3: ADVERSARIAL REVISION (CRITIQUE EACH APPROACH)
        algebraic_critique = await self.revise(
            instruction="""Critically evaluate this algebraic solution:
            - What assumptions does it make? Are they justified?
            - Where are the potential calculation errors?
            - What edge cases does it ignore?
            - Does it fully satisfy the original problem constraints?
            - If flawed, how would you fix it?""",
            context=algebraic_approach
        )

        number_theoretic_critique = await self.revise(
            instruction="""Critically evaluate this number-theoretic solution:
            - What assumptions does it make? Are they justified?
            - Where are the potential calculation errors?
            - What edge cases does it ignore?
            - Does it fully satisfy the original problem constraints?
            - If flawed, how would you fix it?""",
            context=number_theoretic_approach
        )

        geometric_analytic_critique = await self.revise(
            instruction="""Critically evaluate this geometric/analytic solution:
            - What assumptions does it make? Are they justified?
            - Where are the potential calculation errors?
            - What edge cases does it ignore?
            - Does it fully satisfy the original problem constraints?
            - If flawed, how would you fix it?""",
            context=geometric_analytic_approach
        )

        # STEP 4: HIERARCHICAL DECOMPOSITION (IF NEEDED)
        decomposition_instruction = f"""Based on the critiques and classification, decompose the most promising approach into subproblems:
        - Each subproblem should be self-contained but logically dependent
        - Specify prerequisites (which subproblems must be solved first)
        - Focus on conceptual milestones, not just computational steps
        Classification: {classification}
        Critiques: Algebraic: {algebraic_critique} | Number-theoretic: {number_theoretic_critique} | Geometric: {geometric_analytic_critique}"""
        
        subproblems = await self.decompose(
            instruction=decomposition_instruction,
            context=""
        )

        # Solve subproblems in dependency order
        solved_subproblems = {}
        for subproblem in subproblems:
            deps = subproblem.get('dependencies', "").split(',') if subproblem.get('dependencies') else []
            # Wait for dependencies (simplified topological sort)
            for dep_id in deps:
                if dep_id.strip() and dep_id.strip() in solved_subproblems:
                    await asyncio.sleep(0)  # Yield control
            
            solution = await self.generate(
                instruction=f"""Solve this subproblem in isolation:
                {subproblem['description']}
                Use results from these dependencies if needed: {[solved_subproblems.get(dep_id.strip(), '') for dep_id in deps if dep_id.strip()]}
                Be precise and show all steps.""",
                context=json.dumps(subproblem)
            )
            solved_subproblems[subproblem['id']] = solution

        # STEP 5: COMPUTATIONAL VERIFICATION
        verification_code = await self.programmer(
            instruction=f"""Write Python code to verify the most consistent solution from the parallel approaches:
            - Implement brute-force search if solution space is small
            - Implement symbolic verification if algebraic
            - Cross-validate with at least two independent methods
            - Output only the final integer answer (000-999)
            Context: Classification: {classification} | Algebraic: {algebraic_approach} | Number-theoretic: {number_theoretic_approach}""",
            context="",
            max_retries=3
        )

        # STEP 6: SYNTHESIS & CANONICALIZATION
        final_answer = await self.ensemble(
            instruction="""Synthesize the most reliable answer from all sources:
            1. Compare algebraic, number-theoretic, and geometric approaches
            2. Incorporate computational verification result
            3. Resolve contradictions by re-examining problem constraints
            4. Extract the FINAL INTEGER ANSWER (000-999)
            5. If multiple candidates remain, apply problem-specific filters
            6. Output ONLY the 3-digit integer (e.g., '123'), nothing else.""",
            contexts_list=[
                algebraic_approach,
                number_theoretic_approach,
                geometric_analytic_approach,
                verification_code,
                json.dumps(solved_subproblems)
            ]
        )

        # STEP 7: CANONICAL OUTPUT ENFORCEMENT
        canonical_answer = await self.revise(
            instruction="""Ensure the output is a 3-digit integer (000-999):
            - If answer is a number, format as 3-digit string with leading zeros
            - If multiple answers, select the one consistent with all constraints
            - If no valid answer, return '000' and flag error
            - Output ONLY the 3-digit string, no explanations.""",
            context=final_answer
        )

        return canonical_answer.strip()