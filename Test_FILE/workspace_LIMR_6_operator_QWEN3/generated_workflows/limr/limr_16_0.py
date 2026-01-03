# Workflow ID: limr_16_0
# Benchmark: limr
# Data Indices: [187, 210]

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

        # PHASE 1: Problem Classification and Structural Decomposition
        classification = await self.generate(
            instruction="""Perform deep problem classification and structural analysis:
            1. Identify the primary mathematical domain (geometry, combinatorics, number theory, algebra, optimization, etc.)
            2. List all given quantities, constraints, and unknowns
            3. Determine if the problem requires proof, computation, or both
            4. Identify any non-obvious transformations or insights that might be needed (e.g., coordinate embedding, generating functions, modular reduction)
            5. Note any potential edge cases or special conditions
            Format as a structured analysis with clear section headers.""",
            context=""
        )

        decomposition = await self.decompose(
            instruction="""Decompose the problem into minimal, solvable subproblems:
            - Each subproblem should be self-contained and address one clear mathematical objective
            - Specify dependencies: which subproblems must be solved before others
            - Prioritize foundational subproblems (e.g., 'establish coordinate system' before 'compute distances')
            - Include at least one computational subproblem if numerical answer is required
            - Format each subproblem with clear mathematical intent and prerequisite IDs.""",
            context=classification
        )

        # PHASE 2: Parallel Strategy Generation for Independent Subproblems
        # Identify root subproblems (no dependencies)
        root_subproblems = [sp for sp in decomposition if not sp.get('dependencies', '').strip()]
        
        if not root_subproblems:
            # Fallback: treat entire problem as single unit if decomposition fails
            root_subproblems = [{"id": "fallback", "description": "Solve entire problem holistically", "dependencies": ""}]

        strategy_tasks = []
        for subproblem in root_subproblems:
            # Generate 3 distinct approaches per subproblem
            for approach_type in ["algebraic", "geometric", "combinatorial"]:
                task = self.generate(
                    instruction=f"""Develop a detailed solution strategy for subproblem:
                    Subproblem ID: {subproblem['id']}
                    Description: {subproblem['description']}
                    
                    Approach: {approach_type.upper()} PERSPECTIVE
                    - Outline step-by-step mathematical reasoning
                    - Specify theorems, identities, or computational methods to use
                    - Identify potential pitfalls or assumptions
                    - If applicable, provide symbolic equations or pseudocode
                    - Ensure all steps are justified and logically connected""",
                    context=classification
                )
                strategy_tasks.append(task)
        
        raw_strategies = await asyncio.gather(*strategy_tasks)
        
        # PHASE 3: Strategy Refinement and Computational Preparation
        refined_strategies = []
        for i, strategy in enumerate(raw_strategies):
            refined = await self.revise(
                instruction="""Critically refine this solution strategy:
                - Fill any logical gaps or missing justifications
                - Correct any mathematical errors or inconsistencies
                - Add explicit handling of edge cases mentioned in classification
                - If computational steps are implied, make them explicit and precise
                - Ensure final output format aligns with problem requirements (integer 000-999)""",
                context=strategy
            )
            refined_strategies.append(refined)

        # PHASE 4: Parallel Computation and Symbolic Verification
        computation_results = []
        for strategy in refined_strategies:
            try:
                # Extract computational intent
                computation = await self.programmer(
                    instruction="""Generate and execute Python code to compute the numerical result:
                    - Translate mathematical steps into precise code
                    - Handle edge cases explicitly
                    - Ensure output is an integer between 000 and 999
                    - If symbolic computation is needed, use sympy appropriately
                    - Return only the final integer result, nothing else""",
                    context=strategy,
                    max_retries=3
                )
                computation_results.append(computation)
            except Exception:
                # If computation fails, store the symbolic strategy for ensemble to handle
                computation_results.append(f"COMPUTATION_FAILED: {strategy[:500]}...")

        # PHASE 5: Ensemble Synthesis and Contradiction Resolution
        final_answer = await self.ensemble(
            instruction="""Synthesize the best answer from all strategies:
            - Compare numerical results from successful computations
            - If results conflict, identify which strategy has the most rigorous justification
            - For failed computations, evaluate the symbolic reasoning for soundness
            - Resolve contradictions by cross-validating against problem constraints
            - Select or synthesize the single most reliable answer
            - Ensure final answer is an integer between 000 and 999
            - If uncertainty remains, choose the answer with the most robust derivation""",
            contexts_list=computation_results + refined_strategies  # Include both computed and symbolic
        )

        # PHASE 6: Final Verification and Output Formatting
        verified_answer = await self.revise(
            instruction="""Final verification and formatting:
            - Confirm the answer is an integer between 000 and 999
            - Verify it satisfies all original problem constraints
            - If answer is not in correct format, extract the numerical value
            - Return ONLY the three-digit integer (e.g., '042', '123', '999') with no additional text""",
            context=final_answer
        )

        # Extract just the three-digit number using regex as final safeguard
        match = re.search(r'\b(\d{3})\b', verified_answer)
        if match:
            return match.group(1)
        else:
            # Fallback: extract any number and pad to 3 digits
            numbers = re.findall(r'\d+', verified_answer)
            if numbers:
                return numbers[0].zfill(3)[-3:]
            else:
                return "000"  # Ultimate fallback