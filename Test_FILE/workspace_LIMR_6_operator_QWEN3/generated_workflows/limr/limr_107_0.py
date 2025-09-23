# Workflow ID: limr_107_0
# Benchmark: limr
# Data Indices: [71, 326]

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

        # Step 1: Deep Structural Analysis
        structural_analysis = await self.generate(
            instruction="""Perform a deep structural analysis of the problem. Identify:
            - The mathematical domain (algebra, combinatorics, geometry, number theory, etc.)
            - Key variables, constraints, and objectives
            - Symmetries, invariants, or recursive structures
            - The type of answer expected (integer, fraction, proof, etc.)
            - Any hidden assumptions or boundary conditions
            - Potential solution strategies (analytical, computational, combinatorial, etc.)
            Format your response as a structured report with clear headings.""",
            context=""
        )

        # Step 2: Intelligent Decomposition
        subproblems = await self.decompose(
            instruction="""Decompose the problem into logically coherent subproblems. For each subproblem:
            - Provide a clear, self-contained description
            - Specify dependencies on other subproblems (if any)
            - Indicate whether it is primarily analytical, computational, or conceptual
            Prioritize decomposition that isolates computationally tractable parts and insight-driven parts separately.""",
            context=structural_analysis
        )

        # Step 3: Initialize Solution Ledger
        solution_ledger = f"STRUCTURAL ANALYSIS:\n{structural_analysis}\n\nSUBPROBLEMS:\n"
        for sp in subproblems:
            solution_ledger += f"ID {sp['id']}: {sp['description']} (Depends on: {sp['dependencies']})\n"

        # Step 4: Dynamic Strategy Routing & Parallel Execution
        async def solve_subproblem(sp_id, description, dependencies):
            # Classify subproblem type
            classification = await self.generate(
                instruction=f"""Classify this subproblem for optimal solving strategy:
                Subproblem: {description}
                
                Choose one primary strategy:
                A) Analytical Reasoning (use Generate + Revise for symbolic manipulation, proofs, inequalities)
                B) Computational (use Programmer for algorithms, matrix ops, recursion, enumeration)
                C) Hybrid (combine Generate and Programmer)
                
                Justify your choice and outline the specific steps you will take.""",
                context=solution_ledger
            )
            
            if "A)" in classification or "Analytical" in classification:
                attempt = await self.generate(
                    instruction=f"""Solve this subproblem analytically:
                    {description}
                    
                    Use rigorous mathematical reasoning. Show all steps. Leverage insights from the structural analysis.
                    If you derive a general formula or inequality, state it clearly.""",
                    context=solution_ledger
                )
                refined = await self.revise(
                    instruction="""Improve this solution:
                    - Fill any logical gaps
                    - Verify algebraic manipulations
                    - Ensure clarity and precision
                    - Cross-check with constraints from the original problem""",
                    context=attempt
                )
                return refined
            elif "B)" in classification or "Computational" in classification:
                code_solution = await self.programmer(
                    instruction=f"""Write and execute Python code to solve:
                    {description}
                    
                    Ensure the code is efficient and handles edge cases. Output must be precise (no floating point errors).
                    If the problem involves large numbers or recursion, use memoization or matrix exponentiation as appropriate.""",
                    context=solution_ledger
                )
                return code_solution
            else:  # Hybrid
                analytical = await self.generate(
                    instruction=f"""Provide analytical insights or simplifications for:
                    {description}""",
                    context=solution_ledger
                )
                code_solution = await self.programmer(
                    instruction=f"""Write code incorporating these analytical insights:
                    Insights: {analytical}
                    Subproblem: {description}""",
                    context=analytical
                )
                return f"ANALYTICAL INSIGHTS:\n{analytical}\n\nCOMPUTATIONAL SOLUTION:\n{code_solution}"

        # Execute subproblems in parallel
        subproblem_tasks = [
            solve_subproblem(sp['id'], sp['description'], sp['dependencies'])
            for sp in subproblems
        ]
        subproblem_results = await asyncio.gather(*subproblem_tasks)

        # Update ledger with results
        for i, result in enumerate(subproblem_results):
            solution_ledger += f"\n\nSOLUTION FOR SUBPROBLEM {subproblems[i]['id']}:\n{result}"

        # Step 5: Synthesize Partial Results
        synthesis = await self.ensemble(
            instruction="""Synthesize all subproblem solutions into a complete, coherent answer to the original problem.
            - Integrate results logically
            - Resolve any inconsistencies or contradictions
            - Ensure all constraints and conditions are satisfied
            - Derive the final answer (must be an integer 000-999)
            If the answer is a fraction m/n in lowest terms, compute m + n.
            Provide a step-by-step justification of the final answer.""",
            contexts_list=[solution_ledger] + subproblem_results
        )

        # Step 6: Validation and Iterative Refinement (up to 2 iterations)
        for iteration in range(2):
            validation = await self.generate(
                instruction=f"""Critically validate this solution:
                {synthesis}
                
                Check for:
                - Logical consistency
                - Computational accuracy
                - Adherence to problem constraints
                - Correct final answer format (integer 000-999)
                If any issues are found, describe them precisely and suggest corrections.
                If no issues, state 'VALIDATED'.""",
                context=solution_ledger
            )
            
            if "VALIDATED" in validation:
                break
            else:
                synthesis = await self.revise(
                    instruction=f"""Revise the solution to fix the following issues:
                    {validation}
                    
                    Maintain all correct parts. Focus only on the identified errors.
                    Ensure the final answer is an integer between 000 and 999.""",
                    context=synthesis
                )

        # Step 7: Final Answer Extraction
        final_answer = await self.generate(
            instruction="""Extract the final integer answer from the solution below.
            The answer must be an integer between 000 and 999.
            If the solution gives a fraction m/n in lowest terms, output m + n.
            If the solution is already an integer, output that integer.
            Output ONLY the integer, with no additional text or explanation.
            
            Solution:
            """ + synthesis,
            context=synthesis
        )

        return final_answer.strip()