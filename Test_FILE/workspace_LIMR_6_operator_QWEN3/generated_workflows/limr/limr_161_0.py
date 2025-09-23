# Workflow ID: limr_161_0
# Benchmark: limr
# Data Indices: [91, 245]

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

        # PHASE 1: PARALLEL EXPLORATION & CLASSIFICATION
        exploration_tasks = [
            self.generate(
                instruction="""Analyze this problem from a GEOMETRY/ALGEBRA perspective:
                - Identify vectors, matrices, projections, or coordinate systems
                - Extract all given equations or transformation rules
                - Propose solution steps using linear algebra or coordinate geometry
                - Flag if problem involves projections, rotations, or transformations""",
                context=""
            ),
            self.generate(
                instruction="""Analyze this problem from a COMBINATORICS/PROBABILITY perspective:
                - Identify counting scenarios, probability spaces, or random variables
                - Extract sample spaces, events, or distribution parameters
                - Propose solution using combinations, permutations, or probability rules
                - Flag if problem involves dice, coins, cards, or selection processes""",
                context=""
            ),
            self.generate(
                instruction="""Analyze this problem from a NUMBER THEORY/ALGEBRA perspective:
                - Identify integers, primes, modular constraints, or Diophantine conditions
                - Extract divisibility rules, congruences, or polynomial equations
                - Propose solution using modular arithmetic, factorization, or algebraic manipulation
                - Flag if problem involves remainders, gcd/lcm, or integer solutions""",
                context=""
            )
        ]
        
        exploration_results = await asyncio.gather(*exploration_tasks)
        
        # Select most relevant approach
        primary_approach = await self.ensemble(
            instruction="""Select the SINGLE MOST RELEVANT problem-solving approach:
            - Choose the analysis that best matches the problem's core structure
            - Prioritize approaches that identify explicit mathematical operations
            - If multiple are equally valid, choose the one with clearest step-by-step plan
            - Return ONLY the selected approach text""",
            contexts_list=exploration_results
        )

        # PHASE 2: HIERARCHICAL DECOMPOSITION
        decomposition = await self.decompose(
            instruction="""Break this problem into minimal, executable subproblems:
            - Each subproblem should be solvable independently if dependencies are met
            - Specify EXACT mathematical operations needed (not just 'calculate X')
            - Include dependencies: which subproblems must be solved before others
            - Format each as: {'id': 'step1', 'description': '...', 'dependencies': 'none' or 'step1,step3'}""",
            context=primary_approach
        )

        # Execute subproblems in dependency order
        solved_subproblems = {}
        max_iterations = 3
        
        for iteration in range(max_iterations):
            remaining_subproblems = [sp for sp in decomposition if sp['id'] not in solved_subproblems]
            if not remaining_subproblems:
                break
                
            # Group subproblems by dependency readiness
            ready_subproblems = []
            for sp in remaining_subproblems:
                deps = sp['dependencies'].split(',') if sp['dependencies'] != 'none' else []
                if all(dep.strip() in solved_subproblems for dep in deps):
                    ready_subproblems.append(sp)
            
            if not ready_subproblems:
                # Deadlock - force solve one subproblem symbolically
                forced = remaining_subproblems[0]
                solution = await self.generate(
                    instruction=f"""Solve this subproblem through pure symbolic reasoning:
                    Subproblem: {forced['description']}
                    Known context: {solved_subproblems}
                    Show all algebraic steps. Return final value or expression.""",
                    context=primary_approach
                )
                solved_subproblems[forced['id']] = solution
                continue
            
            # Solve ready subproblems in parallel
            solve_tasks = []
            for sp in ready_subproblems:
                deps_context = "\n".join([f"{dep_id}: {solved_subproblems[dep_id]}" for dep_id in sp['dependencies'].split(',') if dep_id.strip() in solved_subproblems]) if sp['dependencies'] != 'none' else ""
                
                task = self.programmer(
                    instruction=f"""Solve this mathematical subproblem:
                    {sp['description']}
                    
                    Context from previous steps:
                    {deps_context}
                    
                    Requirements:
                    - Return exact integer or simplified fraction
                    - Show all computational steps in code comments
                    - If symbolic solution needed, use sympy
                    - If impossible, return 'SYMBOLIC_NEEDED'""",
                    context=deps_context,
                    max_retries=2
                )
                solve_tasks.append((sp['id'], task))
            
            # Execute parallel tasks
            results = await asyncio.gather(*[task for _, task in solve_tasks], return_exceptions=True)
            
            # Process results
            for (sp_id, _), result in zip(solve_tasks, results):
                if isinstance(result, Exception) or "SYMBOLIC_NEEDED" in str(result):
                    # Fall back to symbolic generation
                    symbolic_solution = await self.generate(
                        instruction=f"""Solve symbolically:
                        Subproblem: {next(sp['description'] for sp in decomposition if sp['id'] == sp_id)}
                        Context: {deps_context}
                        Show step-by-step algebraic manipulation. Return final expression.""",
                        context=primary_approach
                    )
                    solved_subproblems[sp_id] = symbolic_solution
                else:
                    solved_subproblems[sp_id] = str(result)

        # PHASE 3: SOLUTION SYNTHESIS & ADVERSARIAL VALIDATION
        full_solution = await self.generate(
            instruction=f"""Synthesize complete solution from subproblem results:
            Subproblem solutions: {solved_subproblems}
            Original approach: {primary_approach}
            
            Steps:
            1. Reconstruct the logical flow from subproblems
            2. Show how each result contributes to final answer
            3. Perform final calculation to get integer answer
            4. Format answer as: \\boxed{{integer}}""",
            context=str(solved_subproblems)
        )

        # Adversarial validation loop
        for validation_round in range(3):
            critic = await self.generate(
                instruction=f"""Act as a ruthless mathematics critic:
                - Identify the WEAKEST step in this solution
                - Check for calculation errors, logical gaps, or unjustified assumptions
                - Verify final answer is integer 000-999
                - If perfect, respond 'VERIFIED'
                - Otherwise, describe EXACTLY what's wrong and how to fix it""",
                context=full_solution
            )
            
            if "VERIFIED" in critic:
                break
                
            # Revise based on criticism
            full_solution = await self.revise(
                instruction=f"""Fix the solution based on this criticism:
                Criticism: {critic}
                
                Requirements:
                - Address ALL identified issues
                - Maintain step-by-step clarity
                - Recalculate any suspect values
                - Preserve correct parts of solution""",
                context=full_solution
            )

        # PHASE 4: FINAL VERIFICATION & FORMATTING
        final_answer = await self.programmer(
            instruction=f"""Extract and verify final answer:
            Solution: {full_solution}
            
            Steps:
            1. Parse the final integer answer from \\boxed{{}} notation
            2. Verify it's an integer between 000 and 999
            3. If valid, return ONLY the integer as string
            4. If invalid, return 'RETRY'""",
            context=full_solution,
            max_retries=1
        )

        # Fallback if verification fails
        if "RETRY" in final_answer or not re.match(r'^\d{1,3}$', final_answer.strip()):
            final_answer = await self.generate(
                instruction=f"""Extract final integer answer from this solution:
                {full_solution}
                
                Return ONLY the integer between 000-999, no explanation.
                If uncertain, make best reasonable guess.""",
                context=full_solution
            )
            
            # Ensure 3-digit format
            final_answer = final_answer.strip()
            if final_answer.isdigit():
                final_answer = final_answer.zfill(3)[:3]
            else:
                final_answer = "000"  # Ultimate fallback

        return final_answer