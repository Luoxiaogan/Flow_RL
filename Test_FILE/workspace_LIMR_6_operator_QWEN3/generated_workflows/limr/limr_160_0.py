# Workflow ID: limr_160_0
# Benchmark: limr
# Data Indices: [223, 290]

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

        # STEP 1: Generate multiple mathematical interpretations in parallel
        interpretations = await asyncio.gather(
            self.generate(
                instruction="""Analyze the problem from an ALGEBRAIC perspective:
                - Identify variables, expressions, equations
                - Look for polynomial, series, or functional structures
                - Consider substitutions or transformations
                - Note symmetries or invariants""",
                context=""
            ),
            self.generate(
                instruction="""Analyze the problem from a COMBINATORIAL/NUMBER THEORETIC perspective:
                - Identify counting elements, modular constraints, divisibility
                - Look for primes, congruences, combinatorial identities
                - Consider pigeonhole, inclusion-exclusion, or generating functions
                - Note bounds or extremal conditions""",
                context=""
            ),
            self.generate(
                instruction="""Analyze the problem from a CALCULATIONAL/ALGORITHMIC perspective:
                - Identify explicit computations or iterative processes
                - Consider brute-force bounds, recursive relations, or closed forms
                - Note numerical patterns or sequences
                - Determine if code execution is feasible and safe""",
                context=""
            )
        )

        # STEP 2: For each interpretation, decompose into subproblems
        decomposition_tasks = []
        for i, interpretation in enumerate(interpretations):
            decomposition_tasks.append(
                self.decompose(
                    instruction=f"""Based on this mathematical interpretation:
                    {interpretation}
                    
                    Decompose the problem into minimal, solvable subproblems.
                    For each subproblem:
                    - State precisely what needs to be computed or proven
                    - List dependencies (which subproblems must be solved first)
                    - Indicate if it requires symbolic manipulation, numerical computation, or logical deduction""",
                    context=interpretation
                )
            )
        
        decompositions = await asyncio.gather(*decomposition_tasks)

        # STEP 3: Solve each decomposition path in parallel
        solution_paths = []
        for i, (interpretation, decomposition) in enumerate(zip(interpretations, decompositions)):
            # Serialize decomposition for context
            decomp_str = "\n".join([
                f"Subproblem {d['id']}: {d['description']} (depends on: {d['dependencies']})"
                for d in decomposition
            ])
            
            # Generate solution plan
            plan = await self.generate(
                instruction=f"""Given interpretation:
                {interpretation}
                
                And decomposition:
                {decomp_str}
                
                Create a step-by-step solution plan:
                - Order subproblems by dependency
                - For each, specify method: symbolic, computational, or logical
                - Include verification step for each major result
                - Flag any potential pitfalls or assumptions""",
                context=decomp_str
            )
            
            # Execute plan — dynamically choose operators per subproblem
            # For simplicity, we simulate by generating a full solution attempt per path
            solution_attempt = await self.generate(
                instruction=f"""Execute the solution plan below. Be precise and rigorous.
                Show all work. Verify intermediate results. If computation is needed, 
                either perform it symbolically or explicitly request code generation.
                Final answer must be an integer between 000 and 999.
                
                Plan:
                {plan}""",
                context=plan
            )
            
            # Validate and revise
            validated = await self.revise(
                instruction="""Critically review this solution:
                - Check for arithmetic or logical errors
                - Verify all constraints from original problem are satisfied
                - Ensure final answer is an integer 000-999
                - If error found, correct it and explain the fix""",
                context=solution_attempt
            )
            
            # Summarize to extract key answer and confidence
            summary = await self.summarize(
                instruction="""Extract:
                1. The final numerical answer (must be integer 000-999)
                2. Confidence level (High/Medium/Low) based on verification
                3. One-sentence justification
                Format: "ANSWER: XXX | CONFIDENCE: Y | REASON: Z" """,
                context=validated
            )
            
            solution_paths.append(summary)

        # STEP 4: Ensemble solutions
        final_answer = await self.ensemble(
            instruction="""Select the best answer from the candidates below.
            Prioritize:
            1. High confidence answers
            2. Answers with clear, verifiable reasoning
            3. Consistency across multiple approaches
            
            If all answers disagree and confidence is low, synthesize by:
            - Identifying common sub-results
            - Resolving contradictions via modular checks or edge cases
            - Outputting the most mathematically consistent result
            
            Final output must be exactly: "ANSWER: XXX" where XXX is 000-999 integer.""",
            contexts_list=solution_paths
        )

        # STEP 5: Fallback loop if low confidence or no clear answer
        if "CONFIDENCE: Low" in final_answer or not re.search(r"ANSWER: \d{3}", final_answer):
            # Extract conflicting assumptions
            conflict_analysis = await self.generate(
                instruction="""The previous attempts yielded low-confidence or conflicting results.
                Identify the core points of disagreement or uncertainty.
                Propose 2-3 targeted experiments or checks (e.g., test with small cases, verify modulo, check boundary conditions)
                that could resolve the ambiguity.""",
                context="\n".join(solution_paths)
            )
            
            # Generate revised attempts based on conflict analysis
            revised_attempts = await asyncio.gather(
                *[self.revise(
                    instruction=f"""Revise your solution considering this analysis:
                    {conflict_analysis}
                    
                    Focus on resolving the specific uncertainty mentioned.
                    Re-verify all steps. Output final answer as 'ANSWER: XXX'.""",
                    context=sp
                ) for sp in solution_paths]
            )
            
            # Re-ensemble
            final_answer = await self.ensemble(
                instruction="""Given revised attempts resolving previous conflicts,
                select the most robust answer. Must output 'ANSWER: XXX' with XXX integer 000-999.""",
                contexts_list=revised_attempts
            )

        # STEP 6: Extract and return final integer
        match = re.search(r"ANSWER:\s*(\d{3})", final_answer)
        if match:
            return match.group(1)
        else:
            # Last resort: extract any 3-digit number
            numbers = re.findall(r"\b\d{3}\b", final_answer)
            if numbers:
                return numbers[0]
            else:
                return "000"  # default fallback