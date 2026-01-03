# Workflow ID: limr_37_0
# Benchmark: limr
# Data Indices: [216, 107]

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

        # STAGE 1: DECOMPOSE & CLASSIFY
        decomposition_instruction = """
        Systematically decompose this mathematical problem into atomic subproblems.
        For each subproblem:
        - Identify its mathematical domain (geometry, algebra, number theory, combinatorics, etc.)
        - Specify what needs to be computed or proven
        - List any dependencies on other subproblems
        - Suggest 2-3 potential solution strategies (e.g., coordinate geometry, modular arithmetic, combinatorial counting)
        - Flag if it requires exact computation or symbolic manipulation
        
        Structure output as a numbered list of subproblems with clear dependencies.
        Prioritize identifying the final target (what integer are we solving for?).
        """
        
        subproblems = await self.decompose(
            instruction=decomposition_instruction,
            context=""
        )

        # Extract final target for focus
        target_analysis = await self.generate(
            instruction="""
            Based on the decomposition, clearly state:
            - What is the final numerical answer we are solving for?
            - What form should it take (integer, modulo, count, etc.)?
            - What constraints must it satisfy?
            - What would constitute a successful verification?
            """,
            context=json.dumps(subproblems)
        )

        # STAGE 2: PARALLEL SOLUTION PATHWAYS
        async def solve_subproblem(subproblem_desc: str, subproblem_id: str) -> str:
            """Generate and refine solution for one subproblem"""
            
            # Generate multiple approaches
            approaches = await asyncio.gather(
                self.generate(
                    instruction=f"""
                    Approach 1 for subproblem {subproblem_id}: 
                    Solve using the most straightforward mathematical method.
                    Show all steps clearly. If computation needed, indicate where.
                    """,
                    context=subproblem_desc
                ),
                self.generate(
                    instruction=f"""
                    Approach 2 for subproblem {subproblem_id}: 
                    Solve using an alternative mathematical framework (e.g., if algebraic, try geometric; if combinatorial, try generating functions).
                    Highlight any creative insights or non-obvious transformations.
                    """,
                    context=subproblem_desc
                )
            )
            
            # Refine each approach
            refined_approaches = await asyncio.gather(
                *[self.revise(
                    instruction=f"""
                    Critically review this solution for subproblem {subproblem_id}:
                    - Verify mathematical correctness
                    - Check for calculation errors
                    - Ensure all constraints are satisfied
                    - Simplify where possible
                    - Flag any assumptions made
                    """,
                    context=approach
                ) for approach in approaches]
            )
            
            # Synthesize best solution for this subproblem
            subproblem_solution = await self.ensemble(
                instruction=f"""
                For subproblem {subproblem_id}, select or synthesize the best solution from the candidates.
                Criteria:
                - Mathematical rigor
                - Computational feasibility
                - Alignment with dependencies
                - Simplicity and clarity
                If both are valid, merge insights. Output must include any computed values.
                """,
                contexts_list=refined_approaches
            )
            
            return subproblem_solution

        # Solve all independent subproblems in parallel
        subproblem_solutions = {}
        subproblem_tasks = []
        
        for sp in subproblems:
            sp_id = sp['id']
            sp_desc = sp['description']
            # Only solve if no dependencies or dependencies already solved
            # For simplicity, we'll solve all in parallel and handle dependencies via context
            # In advanced version, we'd topologically sort by dependencies
            task = solve_subproblem(sp_desc, sp_id)
            subproblem_tasks.append(task)
        
        solutions_list = await asyncio.gather(*subproblem_tasks)
        
        # Map solutions to subproblem IDs
        for i, sp in enumerate(subproblems):
            subproblem_solutions[sp['id']] = solutions_list[i]

        # STAGE 3: INTEGRATE & VERIFY
        integration_context = "\n\n".join([
            f"Subproblem {sp['id']}: {subproblem_solutions[sp['id']]}"
            for sp in subproblems
        ])
        
        integrated_solution = await self.generate(
            instruction=f"""
            Integrate all subproblem solutions into a complete answer.
            Steps:
            1. Combine results in logical order (respect dependencies)
            2. Perform any final computations needed
            3. Verify consistency across all parts
            4. Cross-check against original problem constraints
            5. Explicitly state the final integer answer (000-999)
            
            If any inconsistency is found, flag it and propose resolution.
            """,
            context=integration_context
        )
        
        # STAGE 4: COMPUTATIONAL VERIFICATION (where applicable)
        # Extract any computational claims for verification
        computational_verification = await self.generate(
            instruction="""
            Identify any numerical computations or algebraic simplifications in the solution that can be verified by code.
            For each, specify:
            - The exact computation needed
            - Input values
            - Expected output
            Format as JSON list of verification tasks.
            """,
            context=integrated_solution
        )
        
        try:
            verification_tasks = json.loads(computational_verification)
            if isinstance(verification_tasks, list) and len(verification_tasks) > 0:
                verification_results = []
                for task in verification_tasks:
                    code_result = await self.programmer(
                        instruction=f"""
                        Execute this precise computation: {task}
                        Return only the numerical result. Handle edge cases.
                        If symbolic, compute exact value.
                        """,
                        context=integrated_solution
                    )
                    verification_results.append(code_result)
                
                # Revise solution based on verification
                integrated_solution = await self.revise(
                    instruction=f"""
                    Revise the solution based on computational verification results:
                    {verification_results}
                    Correct any discrepancies. Strengthen confidence in final answer.
                    Ensure final output is a 3-digit integer (000-999).
                    """,
                    context=integrated_solution
                )
        except:
            # If parsing fails, proceed without computational verification
            pass

        # STAGE 5: FINAL ENSEMBLE & OUTPUT
        final_answer = await self.ensemble(
            instruction="""
            Extract the final numerical answer from the solution.
            Requirements:
            - Must be an integer between 000 and 999
            - Must be explicitly stated
            - Must be consistent with all problem constraints
            - If multiple candidates, select the most rigorously derived
            - Format as exactly three digits (e.g., 042, not 42)
            
            If no clear answer, return "ERROR" and explain why.
            """,
            contexts_list=[integrated_solution, target_analysis]
        )

        # Final safeguard: ensure 3-digit format
        final_output = await self.revise(
            instruction="""
            Ensure the final answer is formatted as a 3-digit integer (000-999).
            If it's a number, pad with leading zeros if necessary.
            If it's not a number, return 000.
            Output ONLY the 3-digit string, nothing else.
            """,
            context=final_answer
        )

        return final_output.strip()