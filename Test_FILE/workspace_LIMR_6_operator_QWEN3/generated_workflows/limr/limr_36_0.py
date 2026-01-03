# Workflow ID: limr_36_0
# Benchmark: limr
# Data Indices: [58, 212]

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

        # STEP 1: META-COGNITIVE PROBLEM ANALYSIS
        problem_analysis = await self.generate(
            instruction="""Perform a deep structural analysis of this mathematical problem. Your analysis must include:
            1. Problem Type Classification: Is this primarily algebraic, geometric, combinatorial, number-theoretic, or analytical?
            2. Key Mathematical Objects: Identify all functions, variables, domains, constraints, and boundary conditions.
            3. Symmetries and Invariants: Are there periodicities, even/odd symmetries, or conserved quantities?
            4. Potential Solution Strategies: List 3-5 distinct approaches (e.g., substitution, identity application, coordinate transformation, modular arithmetic, generating functions).
            5. Edge Cases and Special Values: What values of variables might cause discontinuities, singularities, or require special handling?
            6. Expected Answer Format: Confirm the answer is an integer 000-999 and what it represents (count, value, index, etc.).
            7. Known Identities or Theorems: List relevant mathematical tools (e.g., trig identities, Fermat's little theorem, inclusion-exclusion).
            Present your analysis in a structured, bullet-point format with clear headings.""",
            context=""
        )

        # STEP 2: HIERARCHICAL DECOMPOSITION
        decomposition = await self.decompose(
            instruction="""Decompose this problem into atomic, solvable subproblems. Guidelines:
            - Each subproblem should require at most one major insight or computation.
            - Specify dependencies: which subproblems must be solved before others?
            - Include a subproblem for edge case handling and boundary verification.
            - Include a subproblem for final answer formatting and integer constraint enforcement.
            - Ensure the decomposition covers all aspects of the original problem.
            Output as a list of dictionaries with 'id', 'description', and 'dependencies'.""",
            context=problem_analysis
        )

        # STEP 3: PARALLEL SUBPROBLEM SOLVING (DIAMOND PATTERN PER SUBPROBLEM)
        async def solve_subproblem(subproblem):
            sub_id = subproblem['id']
            description = subproblem['description']
            
            # Generate three solution approaches in parallel
            approaches = await asyncio.gather(
                self.generate(
                    instruction=f"""ALGEBRAIC APPROACH: Solve subproblem {sub_id}: {description}
                    - Use symbolic manipulation, equation solving, and algebraic identities.
                    - Show all steps explicitly.
                    - Verify intermediate results.
                    - Handle edge cases mentioned in problem analysis.""",
                    context=problem_analysis
                ),
                self.generate(
                    instruction=f"""GEOMETRIC/ANALYTIC APPROACH: Solve subproblem {sub_id}: {description}
                    - Use graphs, symmetries, coordinate systems, or calculus if applicable.
                    - Visualize the problem if helpful.
                    - Leverage periodicity, monotonicity, or convexity.
                    - Cross-validate with algebraic results.""",
                    context=problem_analysis
                ),
                self.generate(
                    instruction=f"""COMPUTATIONAL/NUMERICAL APPROACH: Solve subproblem {sub_id}: {description}
                    - Outline a computational strategy.
                    - Consider using the programmer operator for verification.
                    - Estimate complexity and feasibility.
                    - Identify potential numerical pitfalls.""",
                    context=problem_analysis
                )
            )
            
            # Ensemble the three approaches
            best_solution = await self.ensemble(
                instruction=f"""Synthesize the three solution approaches for subproblem {sub_id}: {description}
                - Compare results for consistency.
                - Resolve discrepancies by cross-verification.
                - Select the most rigorous and complete solution.
                - Ensure all edge cases are handled.
                - Format the solution clearly with key steps highlighted.""",
                contexts_list=approaches
            )
            
            # Revise for correctness and clarity
            revised_solution = await self.revise(
                instruction=f"""Critically revise the solution for subproblem {sub_id}: {description}
                - Verify logical consistency of all steps.
                - Check boundary conditions and edge cases.
                - Ensure no solutions are missed or duplicated.
                - Improve clarity and mathematical rigor.
                - Confirm alignment with overall problem constraints.""",
                context=best_solution
            )
            
            return {
                'id': sub_id,
                'solution': revised_solution,
                'description': description
            }

        # Solve all subproblems in parallel (respecting dependencies would require topological sort - simplified here for independence)
        subproblem_solutions = await asyncio.gather(
            *[solve_subproblem(sp) for sp in decomposition]
        )

        # STEP 4: INTEGRATE SOLUTIONS
        integration_context = "\n\n".join([
            f"Subproblem {sol['id']}: {sol['description']}\nSolution: {sol['solution']}"
            for sol in subproblem_solutions
        ])

        integrated_solution = await self.summarize(
            instruction="""Integrate all subproblem solutions into a complete answer to the original problem.
            - Track variable substitutions and domain transformations.
            - Combine partial results accounting for dependencies.
            - Verify that the final answer satisfies all original constraints.
            - Ensure the answer is an integer between 000 and 999.
            - Present the final answer in the format: "The answer is [integer]".
            - Include a brief justification linking back to key steps.""",
            context=integration_context
        )

        # STEP 5: VALIDATION AND ADAPTIVE REFINEMENT
        validation = await self.generate(
            instruction="""Critically validate the integrated solution:
            - Does the final answer satisfy the original equation or condition?
            - Are all constraints and boundary conditions honored?
            - Is the solution count or value plausible given the problem context?
            - Are there any logical gaps or unverified assumptions?
            If any issues are found, describe them specifically. Otherwise, confirm correctness.""",
            context=f"Problem Analysis:\n{problem_analysis}\n\nIntegrated Solution:\n{integrated_solution}"
        )

        if "issue" in validation.lower() or "error" in validation.lower() or "incorrect" in validation.lower():
            # Refine decomposition based on validation feedback
            refined_decomposition = await self.decompose(
                instruction=f"""Refine the problem decomposition based on validation feedback: {validation}
                - Add missing subproblems.
                - Correct flawed dependencies.
                - Strengthen edge case handling.
                - Ensure complete coverage of solution space.""",
                context=problem_analysis
            )
            
            # Re-solve with refined decomposition (limited to one refinement to prevent infinite loops)
            refined_solutions = await asyncio.gather(
                *[solve_subproblem(sp) for sp in refined_decomposition]
            )
            
            refined_integration = "\n\n".join([
                f"Subproblem {sol['id']}: {sol['description']}\nSolution: {sol['solution']}"
                for sol in refined_solutions
            ])
            
            integrated_solution = await self.summarize(
                instruction="""Integrate refined subproblem solutions into final answer.
                - Address all validation concerns.
                - Ensure mathematical rigor and completeness.
                - Output final answer as integer 000-999 in format: "The answer is [integer]".""",
                context=refined_integration
            )

        # FINAL EXTRACTION AND FORMATTING
        final_answer = await self.revise(
            instruction="""Extract the final integer answer from the solution.
            - The answer must be an integer between 000 and 999.
            - Remove all explanatory text.
            - Output ONLY the three-digit integer (e.g., "042", "123", "999").
            - If answer is single or double digit, pad with leading zeros.""",
            context=integrated_solution
        )

        return final_answer.strip()