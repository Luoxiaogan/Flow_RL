# Workflow ID: limr_99_0
# Benchmark: limr
# Data Indices: [346, 268]

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

        # STEP 1: Generate multiple mathematical perspectives in parallel
        perspective_instructions = [
            "Analyze this problem through an algebraic lens: identify variables, equations, and algebraic structures. Suggest solution strategies involving equation manipulation, substitution, or polynomial properties.",
            "Analyze this problem through a combinatorial/probabilistic lens: identify counting principles, permutations, combinations, or probability distributions. Suggest strategies involving casework, generating functions, or combinatorial identities.",
            "Analyze this problem through a number-theoretic lens: identify modular arithmetic, divisibility, prime factors, or Diophantine structures. Suggest strategies involving congruences, GCD/LCM, or residue classes.",
            "Analyze this problem through a geometric/coordinate lens: identify spatial relationships, coordinate systems, or geometric transformations. Suggest strategies involving coordinate geometry, vector operations, or symmetry exploitation.",
            "Analyze this problem through an optimization/inequality lens: identify maximization/minimization objectives, constraints, or inequality structures. Suggest strategies involving AM-GM, Cauchy-Schwarz, or calculus-based optimization."
        ]
        
        perspectives = await asyncio.gather(
            *[self.generate(instruction=instr, context="") for instr in perspective_instructions]
        )

        # STEP 2: For each perspective, create a solution branch
        async def process_perspective(perspective, idx):
            # Decompose based on perspective
            decomposition = await self.decompose(
                instruction=f"""Decompose the problem into subproblems guided by this perspective:
                {perspective}
                
                Create 3-5 subproblems that logically lead to a solution. Each subproblem should be self-contained and solvable independently where possible. Include dependencies only if absolutely necessary.""",
                context=perspective
            )
            
            # Solve each subproblem
            subproblem_results = []
            for sub in decomposition:
                sub_id = sub['id']
                sub_desc = sub['description']
                deps = sub.get('dependencies', '')
                
                # Wait for dependencies if any (simplified: assume linear order)
                # In practice, you'd build a dependency graph - but for simplicity, we process in order
                solution_attempt = await self.generate(
                    instruction=f"""Solve this subproblem:
                    {sub_desc}
                    
                    Use rigorous mathematical reasoning. Show all steps. If computation is needed, describe exactly what to calculate (but don't compute yet).""",
                    context=perspective
                )
                
                # Check if computation is needed
                needs_computation = await self.generate(
                    instruction=f"""Does this solution require precise numerical computation?
                    Solution: {solution_attempt}
                    
                    Answer only YES or NO.""",
                    context=solution_attempt
                )
                
                if "YES" in needs_computation.upper():
                    computation = await self.programmer(
                        instruction=f"""Generate Python code to compute the exact value needed in this solution:
                        {solution_attempt}
                        
                        The code must output only the final integer result. Handle edge cases. No print statements except the final answer.""",
                        context=solution_attempt
                    )
                    # Extract number from computation result
                    numbers = re.findall(r'\b\d+\b', computation)
                    computed_value = numbers[-1] if numbers else "COMPUTATION_FAILED"
                    solution_attempt = f"{solution_attempt}\n\nCOMPUTED VALUE: {computed_value}"
                
                subproblem_results.append(f"Subproblem {sub_id}: {solution_attempt}")
            
            # Combine subproblem results
            combined = "\n\n".join(subproblem_results)
            return await self.revise(
                instruction="""Refine this solution branch:
                - Verify all steps against original problem constraints
                - Fill any logical gaps
                - Ensure final answer is an integer between 000 and 999
                - If no clear answer, state 'NO_SOLUTION_FOUND'""",
                context=combined
            )

        # Process all perspectives in parallel
        branch_results = await asyncio.gather(
            *[process_perspective(p, i) for i, p in enumerate(perspectives)]
        )

        # STEP 3: Ensemble synthesis with iterative refinement
        current_ensemble = await self.ensemble(
            instruction="""Synthesize these solution branches:
            - Identify consistent results across branches
            - Resolve contradictions through logical reconciliation
            - Combine complementary insights
            - Output the most confident integer answer (000-999)
            - If branches fundamentally disagree, output the answer with strongest mathematical justification""",
            contexts_list=branch_results
        )

        # Refinement loop (up to 3 iterations)
        for refinement_round in range(3):
            validation = await self.generate(
                instruction=f"""Critically validate this solution:
                {current_ensemble}
                
                Check for:
                1. Arithmetic errors
                2. Logical inconsistencies with original problem
                3. Violations of constraints
                4. Non-integer or out-of-range answers
                5. Unjustified assumptions
                
                If any issues found, describe them specifically. Otherwise, output 'VALIDATED'.""",
                context=current_ensemble
            )
            
            if "VALIDATED" in validation.upper():
                break
                
            # Revise with validation feedback
            current_ensemble = await self.revise(
                instruction=f"""Revise solution based on validation feedback:
                Validation Issues: {validation}
                
                Correct all identified errors. Strengthen weak arguments. Recompute if necessary. Maintain integer answer 000-999.""",
                context=current_ensemble
            )

        # STEP 4: Final formatting and extraction
        final_answer = await self.revise(
            instruction="""Extract the final integer answer:
            - Scan the text for the final numerical result
            - Ensure it's an integer between 000 and 999
            - If multiple numbers, choose the one most directly answering the problem
            - If no clear answer, default to 000
            - Output ONLY the 3-digit number (e.g., '123', '007', '999')""",
            context=current_ensemble
        )

        # Ensure 3-digit format
        numbers = re.findall(r'\b\d+\b', final_answer)
        if numbers:
            answer = int(numbers[-1]) % 1000  # Ensure in range
            return f"{answer:03d}"
        else:
            return "000"