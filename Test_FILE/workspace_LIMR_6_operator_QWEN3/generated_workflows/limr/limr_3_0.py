# Workflow ID: limr_3_0
# Benchmark: limr
# Data Indices: [26, 247]

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

    async def run_workflow(self, recursion_depth=0, max_depth=3):
        """
        Meta-Adaptive Recursive Decomposition Engine (MARDE)
        Dynamically decomposes, parallelizes, validates, and synthesizes solutions.
        """
        import asyncio
        import re

        if recursion_depth > max_depth:
            # Fallback: Direct computational attempt
            try:
                direct_solution = await self.programmer(
                    instruction="""Attempt direct computational solution.
                    Use symbolic math if needed. Search for integer answer between 0 and 999.
                    If problem involves variables, sample over reasonable domain.
                    Return only the final integer answer in format: ANSWER: XXX""",
                    context=""
                )
                match = re.search(r"ANSWER:\s*(\d{1,3})", direct_solution)
                if match:
                    return int(match.group(1)) % 1000
                else:
                    return 0  # Fallback answer
            except:
                return 0

        # Step 1: Domain Analysis & Strategy Classification
        domain_analysis = await self.generate(
            instruction="""Perform deep problem classification and strategy planning:
            1. Identify mathematical domain(s): algebra, geometry, number theory, combinatorics, etc.
            2. Estimate complexity: low (direct computation), medium (requires 2-3 steps), high (needs insight/transformation).
            3. List key variables, constraints, and hidden symmetries.
            4. Suggest 2-3 potential solution strategies with pros/cons.
            5. Flag any known pitfalls or common mistakes for this problem type.
            Format as structured markdown with clear sections.""",
            context=""
        )

        # Step 2: Hierarchical Decomposition
        try:
            subproblems = await self.decompose(
                instruction=f"""Decompose into minimal solvable subproblems.
            Use domain analysis for guidance:
            {domain_analysis}
            
            Rules:
            - Each subproblem should be independently solvable or further decomposable.
            - Prioritize subproblems that reduce overall complexity.
            - Include dependencies only if absolutely necessary.
            - Tag each subproblem with estimated difficulty: [EASY], [MEDIUM], [HARD].""",
                context=domain_analysis
            )
        except:
            # Decomposition failed - treat as atomic problem
            subproblems = [{
                "id": "SP1",
                "description": "Solve the entire problem as a single unit.",
                "dependencies": "",
                "tag": "[HARD]"
            }]

        # Step 3: Parallel Solution Attempts for Top-Level or Hard Subproblems
        solution_attempts = []
        subproblem_results = {}

        for sp in subproblems:
            sp_id = sp["id"]
            sp_desc = sp["description"]
            sp_tag = sp.get("tag", "[HARD]")

            if "[EASY]" in sp_tag:
                # Solve directly with Programmer
                try:
                    result = await self.programmer(
                        instruction=f"""Solve this subproblem exactly:
                        {sp_desc}
                        
                        Return only the numerical result. If multiple answers, return the one fitting original problem context.
                        Format: RESULT: <number>""",
                        context=domain_analysis
                    )
                    match = re.search(r"RESULT:\s*([-\d\.]+)", result)
                    if match:
                        subproblem_results[sp_id] = float(match.group(1))
                    else:
                        subproblem_results[sp_id] = 0
                except:
                    subproblem_results[sp_id] = 0
            else:
                # Generate multiple solution approaches in parallel
                approaches = await asyncio.gather(
                    self.generate(
                        instruction=f"""ALGEBRAIC APPROACH:
                        Solve using algebraic manipulation, identities, substitutions.
                        {sp_desc}
                        Show all steps. Box final sub-result as \\boxed{{value}}.""",
                        context=domain_analysis
                    ),
                    self.generate(
                        instruction=f"""GEOMETRIC/INTUITIVE APPROACH:
                        Solve using geometric interpretation, symmetry, or intuitive insight.
                        {sp_desc}
                        Show all steps. Box final sub-result as \\boxed{{value}}.""",
                        context=domain_analysis
                    ),
                    self.generate(
                        instruction=f"""COMPUTATIONAL/BRUTE-FORCE APPROACH:
                        Solve via code-simulatable method. Define search space, step size, constraints.
                        {sp_desc}
                        Describe algorithm clearly. Box final sub-result as \\boxed{{value}}.""",
                        context=domain_analysis
                    )
                )

                # Ensemble to synthesize best answer
                synthesized = await self.ensemble(
                    instruction=f"""Synthesize the three approaches for subproblem: {sp_desc}
                    - Resolve contradictions
                    - Combine complementary insights
                    - Select most mathematically rigorous result
                    - Extract numerical answer. If none, return 0.
                    Format final answer as: SUBRESULT: <number>""",
                    contexts_list=approaches
                )

                match = re.search(r"SUBRESULT:\s*([-\d\.]+)", synthesized)
                if match:
                    subproblem_results[sp_id] = float(match.group(1))
                else:
                    # Fallback: Recursive decomposition
                    if recursion_depth < max_depth:
                        subproblem_results[sp_id] = await self.run_workflow(recursion_depth + 1)
                    else:
                        subproblem_results[sp_id] = 0

        # Step 4: Validate and Integrate Subproblem Results
        integration_context = "\n".join([f"{k}: {v}" for k, v in subproblem_results.items()])
        
        integrated_solution = await self.generate(
            instruction=f"""Integrate subproblem results into final answer:
            Subproblem Results:
            {integration_context}
            
            Original Problem Context:
            {domain_analysis}
            
            Steps:
            1. Verify consistency between subproblem results and original constraints.
            2. Combine results using appropriate mathematical operations.
            3. Ensure final answer is integer between 0 and 999.
            4. Double-check for off-by-one errors, modular mismatches, or domain violations.
            Output ONLY the final answer as: ANSWER: XXX""",
            context=integration_context
        )

        # Step 5: Final Validation and Extraction
        validation = await self.generate(
            instruction=f"""VALIDATE FINAL ANSWER:
            Proposed Solution: {integrated_solution}
            Original Problem: {self.problem_text}
            
            Checklist:
            - Does answer satisfy all problem constraints?
            - Is it in [0, 999]?
            - Is it an integer?
            - Cross-verify with at least one alternative method.
            
            If valid, return: VALID: XXX
            If invalid, return: INVALID and suggest correction.""",
            context=integrated_solution
        )

        match = re.search(r"VALID:\s*(\d{1,3})", validation)
        if match:
            return int(match.group(1)) % 1000
        else:
            # Final fallback: extract any number from integrated solution
            numbers = re.findall(r"\b\d{1,3}\b", integrated_solution)
            if numbers:
                return int(numbers[-1]) % 1000
            else:
                return 0