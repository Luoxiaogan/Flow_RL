# Workflow ID: limr_108_0
# Benchmark: limr
# Data Indices: [347, 221]

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

        # Step 1: Deep structural classification of the problem
        classification = await self.generate(
            instruction="""Perform a deep structural analysis of this mathematical problem. Identify:
            1. Primary domain (algebra, combinatorics, number theory, geometry, etc.)
            2. Key mathematical objects involved (polynomials, radicals, permutations, etc.)
            3. Solution approach category:
               - Direct computation
               - Symbolic manipulation/ansatz
               - Case enumeration
               - Proof-based reasoning
               - Recursive/inductive structure
            4. Expected complexity (number of distinct steps)
            5. Potential pitfalls or non-obvious insights required
            6. Whether Programmer can handle core computation or if symbolic reasoning dominates
            Format as a structured JSON-like outline with clear section headers.""",
            context=""
        )

        # Step 2: Extract classification summary for routing
        route_summary = await self.summarize(
            instruction="""Extract concise routing directives from the classification:
            - Single word for primary domain (e.g., "algebra", "combinatorics")
            - Boolean: "needs_decomposition" (true if >3 interdependent steps)
            - Boolean: "needs_parallel_strategies" (true if solution path is ambiguous)
            - Boolean: "programmer_centric" (true if >70% of work is computational)
            Output as key-value pairs, one per line.""",
            context=classification
        )

        # Step 3: Conditional branching based on classification
        if "combinatorics" in route_summary.lower() or "enumeration" in classification.lower():
            # Combinatorial path: often needs case decomposition
            strategy = await self.generate(
                instruction="""For this combinatorial problem:
                1. Identify all constraints and invariants
                2. Determine if brute-force enumeration is feasible (consider problem size)
                3. If not, propose mathematical shortcuts (symmetry, generating functions, inclusion-exclusion)
                4. Outline step-by-step counting strategy
                Be explicit about edge cases and overcounting risks.""",
                context=classification
            )
            
            # Decompose if needed
            if "needs_decomposition: true" in route_summary.lower():
                subproblems = await self.decompose(
                    instruction="""Break this combinatorial problem into minimal atomic subproblems.
                    Each subproblem should be solvable independently or with specified dependencies.
                    Focus on: 
                    - Constraint isolation
                    - Case partitioning
                    - Modular counting steps
                    Return as numbered list with dependencies.""",
                    context=strategy
                )
                
                # Solve subproblems sequentially
                solutions = []
                for sp in subproblems:
                    sol = await self.generate(
                        instruction=f"""Solve subproblem: {sp['description']}
                        Use previous solutions if dependencies exist: {', '.join(solutions[-1:] if solutions else [])}
                        Show all reasoning steps.""",
                        context=strategy
                    )
                    solutions.append(sol)
                
                combined = await self.ensemble(
                    instruction="""Synthesize subproblem solutions into final answer.
                    Ensure consistency across cases. Verify no overlaps or gaps in counting.
                    Extract final integer answer between 000-999.""",
                    contexts_list=solutions
                )
            else:
                # Direct solution attempt
                attempt = await self.generate(
                    instruction="""Execute the combinatorial strategy outlined.
                    Show all steps. Pay special attention to:
                    - Distinguishable vs indistinguishable elements
                    - Constraint satisfaction
                    - Overcounting correction
                    End with boxed final answer.""",
                    context=strategy
                )
                combined = attempt

        elif "algebra" in route_summary.lower() or "symbolic" in classification.lower():
            # Algebraic path: often needs ansatz + verification
            parallel_strategies = await asyncio.gather(
                self.generate(
                    instruction="""Strategy 1: Assume solution form (e.g., a√2 + b√3 + c√5).
                    Derive equations by squaring/expanding. Solve system for integer coefficients.
                    Show all algebraic manipulations.""",
                    context=classification
                ),
                self.generate(
                    instruction="""Strategy 2: Look for field norm or conjugate properties.
                    Multiply by conjugates to rationalize. Extract coefficients systematically.
                    Consider minimal polynomials if applicable.""",
                    context=classification
                ),
                self.generate(
                    instruction="""Strategy 3: Numerical approximation + integer relation detection.
                    Compute decimal value, then use PSLQ or lattice reduction to guess integer coefficients.
                    Verify symbolically afterward.""",
                    context=classification
                )
            )
            
            # Synthesize best approach
            combined = await self.ensemble(
                instruction="""Evaluate all algebraic strategies:
                - Which has most rigorous derivation?
                - Which can be computationally verified?
                - Which matches problem constraints (positive integers, etc.)?
                Select and refine the optimal path. Extract final a*b*c or equivalent integer.""",
                contexts_list=parallel_strategies
            )

        else:
            # Default path: hierarchical decomposition + programmer assist
            decomposition = await self.decompose(
                instruction="""Break problem into minimal solvable subproblems.
                Prioritize:
                1. Isolating computational vs symbolic steps
                2. Creating verifiable intermediate results
                3. Enabling Programmer for precise calculations
                Return as dependency-ordered list.""",
                context=classification
            )
            
            solutions = []
            for sp in decomposition:
                # Check if this subproblem is computational
                is_computational = await self.generate(
                    instruction=f"""Is subproblem '{sp['description']}' primarily computational?
                    (i.e., can be solved by algorithm, equation solving, or counting)
                    Answer only 'yes' or 'no'.""",
                    context=sp['description']
                )
                
                if "yes" in is_computational.lower():
                    sol = await self.programmer(
                        instruction=f"""Solve this subproblem computationally:
                        {sp['description']}
                        Return only the numerical result or minimal code output.""",
                        context=""
                    )
                else:
                    sol = await self.generate(
                        instruction=f"""Solve symbolically: {sp['description']}
                        Show all reasoning. Reference prior solutions if needed: {', '.join(solutions)}""",
                        context=classification
                    )
                solutions.append(sol)
            
            combined = await self.ensemble(
                instruction="""Integrate all subproblem solutions.
                Verify consistency. Extract final integer answer 000-999.
                If multiple candidates exist, select most mathematically rigorous.""",
                contexts_list=solutions
            )

        # Step 4: Adversarial validation
        validated = await self.revise(
            instruction="""Critically review this solution:
            1. Are all steps mathematically sound?
            2. Are there arithmetic errors or logical gaps?
            3. Does the final answer satisfy problem constraints?
            4. If any doubt exists, propose corrections.
            If no errors found, output 'VERIFIED: [original answer]'.""",
            context=combined
        )

        # Step 5: Extract final answer
        final_answer = await self.generate(
            instruction="""Extract ONLY the final integer answer from 000 to 999.
            If multiple numbers appear, select the one that is the primary solution.
            If no clear answer, return 000.
            Output format: exactly three digits, no text.""",
            context=validated
        )

        # Ensure 3-digit format
        match = re.search(r'\b(\d{1,3})\b', final_answer)
        if match:
            num = int(match.group(1))
            return f"{num:03d}"
        else:
            return "000"