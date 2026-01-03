# Workflow ID: limr_84_0
# Benchmark: limr
# Data Indices: [243, 81]

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

        # PHASE 1: PROBLEM DECOMPOSITION & STRATEGY GENERATION
        decomposition = await self.decompose(
            instruction="""Break this problem into fundamental subproblems. For each:
            1. Identify the mathematical domain (algebra, combinatorics, geometry, etc.)
            2. Specify what needs to be computed or proven
            3. Note any key constraints or symmetries
            4. Suggest potential strategies or theorems that might apply
            5. Indicate dependencies between subproblems
            Return as structured list with 'id', 'description', and 'dependencies'.""",
            context=""
        )

        # PHASE 2: PARALLEL STRATEGY EXPLORATION
        strategy_contexts = []
        for subproblem in decomposition:
            strategy = await self.generate(
                instruction=f"""For subproblem: {subproblem['description']}
                Generate 2-3 distinct solution approaches. For each:
                - Outline the key steps
                - Identify potential pitfalls or assumptions
                - Specify whether it requires symbolic manipulation, numerical computation, or logical deduction
                - Note any required mathematical tools (e.g., AM-GM inequality, generating functions, modular arithmetic)
                Prioritize creative, non-obvious approaches that exploit problem structure.""",
                context=""
            )
            strategy_contexts.append(strategy)

        # PHASE 3: PARALLEL SUBPROBLEM SOLVING
        solution_attempts = []
        for i, (subproblem, strategy) in enumerate(zip(decomposition, strategy_contexts)):
            # Try multiple approaches per subproblem
            approaches = strategy.split('\n\n')[:3]  # Take up to 3 approaches
            approach_solutions = []
            
            for j, approach in enumerate(approaches):
                if not approach.strip():
                    continue
                    
                # First attempt: guided symbolic/analytical solution
                analytical_attempt = await self.generate(
                    instruction=f"""Implement this approach for subproblem {subproblem['id']}:
                    {approach}
                    
                    Show all steps clearly. If you reach an impasse, explain why and suggest an alternative.
                    If the approach requires computation, specify exactly what needs to be calculated.""",
                    context=strategy
                )
                
                # If computation is needed, use programmer
                if any(keyword in analytical_attempt.lower() for keyword in ['calculate', 'compute', 'numerical', 'value of']):
                    try:
                        computation = await self.programmer(
                            instruction=f"""Based on this analytical work:
                            {analytical_attempt}
                            
                            Write Python code to perform the required computation. 
                            - Use exact arithmetic where possible
                            - Handle edge cases
                            - Return results in a clear, labeled format
                            - If multiple values, return as JSON""",
                            context=analytical_attempt,
                            max_retries=3
                        )
                        # Revise analytical attempt with computed results
                        analytical_attempt = await self.revise(
                            instruction=f"""Incorporate these computational results:
                            {computation}
                            
                            Update your solution with the computed values. Ensure all steps remain logically sound.""",
                            context=analytical_attempt
                        )
                    except Exception as e:
                        # Fallback: try different approach
                        continue
                
                approach_solutions.append(analytical_attempt)
            
            # Ensemble best solution for this subproblem
            if len(approach_solutions) > 1:
                best_solution = await self.ensemble(
                    instruction=f"""Select the most complete and correct solution for subproblem {subproblem['id']}.
                    Criteria:
                    1. Mathematical rigor and correctness
                    2. Completeness of steps
                    3. Alignment with problem constraints
                    4. Elegance and efficiency
                    Justify your selection.""",
                    contexts_list=approach_solutions
                )
            elif approach_solutions:
                best_solution = approach_solutions[0]
            else:
                # Fallback: generate new attempt
                best_solution = await self.generate(
                    instruction=f"""Generate a comprehensive solution for subproblem: {subproblem['description']}
                    Use fundamental principles. Show all work. Verify each step.""",
                    context=""
                )
            
            solution_attempts.append({
                'subproblem_id': subproblem['id'],
                'solution': best_solution,
                'original_description': subproblem['description']
            })

        # PHASE 4: SOLUTION SYNTHESIS
        synthesis_context = "\n\n".join([
            f"Subproblem {attempt['subproblem_id']}: {attempt['original_description']}\nSolution: {attempt['solution']}"
            for attempt in solution_attempts
        ])

        synthesized_solution = await self.generate(
            instruction="""Synthesize all subproblem solutions into a complete, coherent answer to the original problem.
            - Show how subproblem solutions connect
            - Resolve any apparent contradictions
            - Derive the final answer step by step
            - Ensure the final answer is an integer between 000 and 999
            - Box the final answer in \\boxed{} format""",
            context=synthesis_context
        )

        # PHASE 5: RIGOROUS VALIDATION & REFINEMENT
        validated_solution = await self.revise(
            instruction="""Critically review this solution:
            1. Verify each mathematical step for correctness
            2. Check that all problem constraints are satisfied
            3. Ensure the final answer is an integer between 000 and 999
            4. Look for calculation errors or logical gaps
            5. Confirm that the solution path is complete and justified
            If any issues are found, correct them and explain the fix.""",
            context=synthesized_solution
        )

        # PHASE 6: FINAL EXTRACTION & FORMATTING
        final_answer = await self.generate(
            instruction="""Extract the final numerical answer from this solution.
            - The answer must be an integer between 000 and 999
            - If multiple candidates exist, select the one best supported by the mathematics
            - Format as a 3-digit string with leading zeros if necessary (e.g., '042')
            - If uncertain, explain why and provide your best judgment
            Return ONLY the 3-digit string, nothing else.""",
            context=validated_solution
        )

        # Ensure proper formatting
        final_answer = final_answer.strip()
        if len(final_answer) > 3:
            # Extract first 3-digit number found
            import re
            matches = re.findall(r'\b\d{1,3}\b', final_answer)
            if matches:
                final_answer = matches[0].zfill(3)[-3:]
            else:
                final_answer = "000"  # fallback
        
        final_answer = final_answer.zfill(3)[-3:]  # Ensure 3 digits
        
        return final_answer