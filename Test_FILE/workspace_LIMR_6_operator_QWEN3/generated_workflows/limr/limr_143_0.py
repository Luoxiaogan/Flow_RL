# Workflow ID: limr_143_0
# Benchmark: limr
# Data Indices: [239, 226]

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

        # STEP 1: INITIAL DECOMPOSITION & DOMAIN CLASSIFICATION
        decomposition = await self.decompose(
            instruction="""Break down the problem into atomic subproblems. For each:
            - Assign a unique ID
            - Describe the mathematical task (be specific: e.g., 'solve Diophantine equation', 'count lattice points')
            - Classify by domain: Algebra, Number Theory, Combinatorics, Geometry, Probability, Optimization
            - List dependencies (other subproblem IDs this relies on)
            - Flag if it requires creative insight or non-obvious transformation
            Output as structured list of dictionaries.""",
            context=""
        )

        # STEP 2: PARALLEL PERSPECTIVE GENERATION (DIAMOND PATTERN START)
        algebraic_perspective = await self.generate(
            instruction="""Analyze the problem through an algebraic lens:
            - Identify all variables, equations, and functional relationships
            - Look for symmetries, substitutions, or transformations that simplify structure
            - Note any polynomial, exponential, or recursive patterns
            - Suggest potential algebraic techniques (e.g., Vieta's, generating functions, induction)
            Output detailed analysis with clear section headers.""",
            context=""
        )

        combinatorial_perspective = await self.generate(
            instruction="""Analyze the problem through a combinatorial/probabilistic lens:
            - Identify counting elements: objects, arrangements, selections, probabilities
            - Look for overcounting/undercounting risks, symmetries, or invariants
            - Suggest combinatorial principles: inclusion-exclusion, pigeonhole, linearity of expectation
            - Flag any hidden bijections or recursive structures
            Output detailed analysis with clear section headers.""",
            context=""
        )

        structural_perspective = await self.generate(
            instruction="""Analyze the problem through a structural/number-theoretic/geometric lens:
            - Identify constraints, modular conditions, divisibility, or geometric invariants
            - Look for prime factorizations, gcd/lcm relationships, or coordinate transformations
            - Suggest structural techniques: modular arithmetic, vector geometry, extremal principles
            - Flag any boundary cases or degenerate configurations
            Output detailed analysis with clear section headers.""",
            context=""
        )

        # STEP 3: REVISE & DEEPEN EACH PERSPECTIVE
        perspectives = [algebraic_perspective, combinatorial_perspective, structural_perspective]
        deepened_perspectives = await asyncio.gather(*[
            self.revise(
                instruction=f"""Deepen this analysis:
                - Add missing mathematical rigor: specify theorems, identities, or lemmas used
                - Include concrete examples or small cases to illustrate key insights
                - Explicitly state any assumptions or constraints
                - Connect insights to the original problem's requirements
                Original perspective: {perspective}""",
                context=perspective
            ) for perspective in perspectives
        ])

        # STEP 4: ENSEMBLE INTO UNIFIED PROBLEM MAP
        problem_map = await self.ensemble(
            instruction="""Synthesize all perspectives into a unified problem understanding:
            - Identify overlapping insights and conflicting interpretations
            - Map subproblems from decomposition to relevant perspectives
            - Highlight the most promising solution paths and potential pitfalls
            - Classify the problem's primary domain and required techniques
            - Output as structured summary with sections: Key Insights, Solution Paths, Risks, Recommended Approach""",
            contexts_list=deepened_perspectives
        )

        # STEP 5: CONDITIONAL BRANCHING BASED ON PROBLEM TYPE
        classification = await self.generate(
            instruction=f"""Based on the problem map below, classify and route:
            {problem_map}

            Output JSON-like structure with keys:
            - "primary_domain": (Algebra, Number Theory, Combinatorics, Geometry, Probability, Optimization)
            - "secondary_domains": list of other relevant domains
            - "requires_computation": boolean (true if brute-force or numerical verification needed)
            - "creative_leap_required": boolean (true if non-obvious insight is critical)
            - "recommended_approach": short description of best strategy
            Be precise and justify each classification.""",
            context=problem_map
        )

        # Parse classification (robustly)
        try:
            # Extract JSON-like parts
            if "