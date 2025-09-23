# Workflow ID: limr_10_0
# Benchmark: limr
# Data Indices: [252, 342]

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

        # === PHASE 1: PARALLEL PROBLEM CLASSIFICATION ===
        classification_instructions = [
            """Analyze this problem from an ALGEBRAIC perspective:
            - Identify all variables, equations, and functional relationships
            - Determine if polynomial, functional equation, or system of equations
            - Note symmetry, substitution opportunities, or invariant quantities
            - Suggest algebraic techniques: factoring, Vieta, substitution, etc.
            Output structured analysis.""",
            
            """Analyze this problem from a GEOMETRIC/ANALYTIC perspective:
            - Identify if spatial, coordinate, or transformation-based
            - Look for implicit geometric constraints or symmetries
            - Suggest coordinate assignment, vector approaches, or trigonometric identities
            - Note if 2D/3D, conic sections, or complex plane representations
            Output structured analysis.""",
            
            """Analyze this problem from a COMBINATORIAL/NUMBER THEORETIC perspective:
            - Identify counting elements, modular constraints, or divisibility
            - Look for patterns, sequences, or recursive structures
            - Suggest generating functions, modular arithmetic, or combinatorial identities
            - Note primes, factorizations, or Diophantine constraints
            Output structured analysis."""
        ]

        classifications = await asyncio.gather(
            *[self.generate(instr, "") for instr in classification_instructions]
        )

        # Synthesize classifications into unified problem understanding
        problem_understanding = await self.ensemble(
            instruction="""Synthesize these three mathematical perspectives into one coherent problem analysis:
            - Identify the dominant mathematical domain (algebra, geometry, combinatorics, etc.)
            - List all key constraints and variables
            - Highlight any hidden symmetries or invariants
            - Propose the most promising 2-3 solution strategies
            - Flag any potential pitfalls or edge cases
            Output must be comprehensive and actionable.""",
            contexts_list=classifications
        )

        # === PHASE 2: HIERARCHICAL DECOMPOSITION ===
        decomposition = await self.decompose(
            instruction="""Decompose this problem into minimal solvable subproblems:
            - Each subproblem should be mathematically atomic (solvable with one technique)
            - Label each with domain: [ALGEBRA, GEOMETRY, COMBINATORICS, CALCULUS, NUMBER_THEORY]
            - Specify dependencies: which subproblems must be solved before others
            - Include at least one computational subproblem if applicable
            - Ensure coverage: no part of original problem left unaddressed
            Format: List of dicts with 'id', 'description', 'dependencies', 'domain'""",
            context=problem_understanding
        )

        # Build solution dossier (accumulated context)
        solution_dossier = await self.summarize(
            instruction="""Create a 'solution dossier' from the decomposition:
            - List all subproblems with their domains and dependencies
            - Extract all key variables and constraints
            - Note any computational subproblems requiring code
            - Format as clear, bullet-pointed reference for subsequent steps""",
            context=str(decomposition)
        )

        # === PHASE 3: PARALLEL SOLUTION ATTEMPTS ===
        solution_strategies = [
            """Solve using PURE ALGEBRAIC MANIPULATION:
            - Follow dependency order from decomposition
            - Show all symbolic steps explicitly
            - Justify each transformation
            - Verify intermediate results against constraints
            - If stuck, note assumption and proceed conditionally""",
            
            """Solve using COMPUTATIONAL/PROGRAMMATIC APPROACH:
            - Identify subproblems suitable for code (marked 'COMPUTATIONAL')
            - Generate Python code for those subproblems
            - Use symbolic math (sympy) where possible
            - For infinite processes, compute partial results and extrapolate
            - Return code + output + interpretation""",
            
            """Solve using TRANSFORMATION/ANALOGY:
            - Transform problem into different domain (e.g., geometric to algebraic)
            - Use known theorems or analogous problems as templates
            - Look for invariant quantities or conserved properties
            - If direct solution fails, solve dual problem and map back"""
        ]

        # Generate parallel solution attempts
        raw_solutions = await asyncio.gather(
            *[self.generate(instr, solution_dossier) for instr in solution_strategies]
        )

        # === PHASE 4: ADVERSARIAL REVISION ===
        revised_solutions = []
        for i, solution in enumerate(raw_solutions):
            revised = await self.revise(
                instruction=f"""CRITICALLY REVISE this solution attempt #{i+1}:
                - Verify all mathematical steps for logical consistency
                - Check boundary cases: n=0, negative values, limits, edge conditions
                - Validate against original problem constraints
                - Identify any hidden assumptions and test their necessity
                - If computational, verify precision and convergence
                - If symbolic, check for algebraic errors or division by zero
                - Output must include confidence score (0-100%) and justification""",
                context=solution
            )
            revised_solutions.append(revised)

        # === PHASE 5: META-REASONING ENSEMBLE ===
        final_answer = await self.ensemble(
            instruction="""SELECT AND SYNTHESIZE the best solution:
            - Compare all revised solutions on: rigor, completeness, elegance, and correctness
            - Prefer solutions with explicit verification and edge-case handling
            - If conflict, identify root cause and resolve using first principles
            - Extract final numerical answer (must be integer 000-999)
            - If answer is fractional, reduce and take numerator/denominator as appropriate
            - If negative, take absolute value unless context forbids
            - If >999, take modulo 1000
            - Format as exactly three digits (zero-padded)
            - Include one-sentence justification""",
            contexts_list=revised_solutions
        )

        # === PHASE 6: FINAL EXTRACTION AND FORMATTING ===
        extracted_answer = await self.generate(
            instruction="""EXTRACT AND FORMAT FINAL ANSWER:
            - From the ensemble output, extract ONLY the three-digit integer
            - Remove all text, keep only digits
            - If no clear answer, return '000' as fallback
            - Output must be exactly three digits, nothing else""",
            context=final_answer
        )

        # Clean and return
        clean_answer = re.sub(r'\D', '', extracted_answer.strip())[:3]
        while len(clean_answer) < 3:
            clean_answer = '0' + clean_answer

        return clean_answer