# Workflow ID: limr_88_0
# Benchmark: limr
# Data Indices: [67, 143]

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

        # Step 1: Initial problem analysis and strategy generation
        initial_analysis = await self.generate(
            instruction="""Perform a deep structural analysis of this mathematical problem. Identify:
            - The primary mathematical domain (algebra, geometry, combinatorics, number theory, etc.)
            - Key variables, constraints, and symmetries
            - Potential solution strategies (e.g., polynomial identities, geometric transformations, combinatorial counting)
            - Whether the problem naturally decomposes into subproblems
            - Any known theorems or identities that might apply
            - Expected form of the answer (must be integer 000-999)
            
            Then, propose a detailed solution strategy plan that includes:
            - Recommended first steps
            - Potential pitfalls or tricky aspects
            - Whether computational verification is feasible
            - Alternative approaches if primary strategy fails
            
            Format your response as a structured plan with clear sections.""",
            context=""
        )

        # Step 2: Parallel decomposition and brute-force computational attempt
        decomposition_task = self.decompose(
            instruction="""Decompose this problem into the smallest possible set of interdependent subproblems.
            For each subproblem:
            - Clearly state what needs to be solved
            - Identify dependencies on other subproblems
            - Estimate difficulty (low/medium/high)
            - Suggest a solution method
            
            Only decompose if the problem has clear, logical subcomponents. If the solution requires a single insight, return an empty list.""",
            context=initial_analysis
        )

        computational_attempt = self.programmer(
            instruction="""Attempt to solve this problem computationally. Generate Python code that:
            - Models the mathematical scenario described
            - Performs necessary calculations or simulations
            - Returns an integer answer between 000 and 999
            - Includes validation checks for edge cases
            
            If the problem is not amenable to direct computation (e.g., requires symbolic manipulation or proof), return 'NOT_COMPUTABLE'.""",
            context=initial_analysis
        )

        # Execute parallel tasks
        decomposition_result, computational_result = await asyncio.gather(
            decomposition_task, 
            computational_attempt
        )

        # Step 3: Strategy selection based on decomposition and computational results
        if "NOT_COMPUTABLE" not in computational_result and re.search(r'\b\d{3}\b', computational_result):
            # Computational approach succeeded - use it as primary candidate
            primary_candidate = computational_result
            # Still generate analytical solution for verification
            analytical_strategy = "Generate analytical solution for verification"
        elif isinstance(decomposition_result, list) and len(decomposition_result) > 0:
            # Problem decomposes well - solve hierarchically
            analytical_strategy = "Solve using hierarchical decomposition"
        else:
            # Neither computation nor decomposition worked - use parallel analytical approaches
            analytical_strategy = "Explore multiple analytical approaches in parallel"

        # Step 4: Generate solution based on selected strategy
        if analytical_strategy == "Generate analytical solution for verification":
            analytical_solution = await self.generate(
                instruction=f"""Based on the initial analysis:
                {initial_analysis}
                
                Generate a complete analytical solution to verify the computational result: {computational_result}
                - Show all mathematical steps
                - Justify each transformation
                - Ensure final answer is an integer 000-999
                - Cross-validate with computational result""",
                context=initial_analysis
            )
            solution_candidates = [computational_result, analytical_solution]
            
        elif analytical_strategy == "Solve using hierarchical decomposition":
            # Solve subproblems in dependency order
            solved_subproblems = {}
            for subproblem in sorted(decomposition_result, key=lambda x: len(x.get('dependencies', '').split(',')) if x.get('dependencies') else 0):
                subproblem_id = subproblem['id']
                dependencies = subproblem.get('dependencies', '').split(',') if subproblem.get('dependencies') else []
                
                # Wait for dependencies to be solved
                dependency_context = "\n".join([f"Subproblem {dep}: {solved_subproblems.get(dep, 'Not solved yet')}" for dep in dependencies if dep in solved_subproblems])
                
                solution = await self.generate(
                    instruction=f"""Solve this subproblem as part of a larger solution:
                    {subproblem['description']}
                    
                    Dependencies: {dependency_context}
                    
                    Initial problem analysis: {initial_analysis}
                    
                    Provide complete solution with all steps. Final output should be clear and self-contained.""",
                    context=dependency_context
                )
                solved_subproblems[subproblem_id] = solution
            
            # Synthesize final solution from subproblems
            synthesis_context = "\n\n".join([f"Subproblem {k}: {v}" for k, v in solved_subproblems.items()])
            analytical_solution = await self.generate(
                instruction=f"""Synthesize a complete solution to the original problem from these solved subproblems:
                {synthesis_context}
                
                Ensure the final answer is an integer between 000 and 999. Show how subproblem solutions combine to form the final answer.""",
                context=synthesis_context
            )
            solution_candidates = [analytical_solution]
            
        else:  # analytical_strategy == "Explore multiple analytical approaches in parallel"
            # Generate 3 different analytical approaches in parallel
            approach_instructions = [
                """Approach 1: Algebraic Manipulation
                - Look for symmetries, substitutions, or identities
                - Consider polynomial, trigonometric, or exponential transformations
                - Simplify step by step with rigorous justification""",
                
                """Approach 2: Geometric or Visual Interpretation
                - Can the problem be represented geometrically?
                - Are there vectors, coordinates, or diagrams that clarify the situation?
                - Use spatial reasoning or coordinate geometry""",
                
                """Approach 3: Combinatorial or Number Theoretic
                - Count possibilities, use modular arithmetic, or apply number theory
                - Look for patterns, recurrences, or combinatorial identities
                - Consider edge cases and special values"""
            ]
            
            analytical_approaches = await asyncio.gather(
                *[self.generate(
                    instruction=f"""{approach_instr}
                    
                    Based on initial analysis: {initial_analysis}
                    
                    Provide complete solution with all steps. Final answer must be integer 000-999.""",
                    context=initial_analysis
                ) for approach_instr in approach_instructions]
            )
            solution_candidates = analytical_approaches

        # Step 5: Validate and refine solutions
        validated_solutions = []
        for i, candidate in enumerate(solution_candidates):
            # Extract potential answer
            answer_match = re.search(r'\b\d{3}\b', candidate)
            if answer_match:
                extracted_answer = answer_match.group(0)
                # Validate by generating verification code
                verification_code = await self.programmer(
                    instruction=f"""Generate Python code to verify that {extracted_answer} is the correct answer to the original problem.
                    The code should:
                    - Implement a direct check or alternative calculation
                    - Return True if answer is correct, False otherwise
                    - Handle edge cases
                    
                    If verification is not possible, return 'CANNOT_VERIFY'.""",
                    context=candidate
                )
                
                if "CANNOT_VERIFY" not in verification_code and ("True" in verification_code or "true" in verification_code.lower()):
                    validated_solutions.append(candidate)
                else:
                    # Attempt to revise the solution
                    revised = await self.revise(
                        instruction=f"""Revise this solution to fix potential errors:
                        - Check all mathematical steps
                        - Ensure answer is integer 000-999
                        - Cross-validate with other approaches if available
                        - Improve clarity and rigor
                        
                        Original solution: {candidate}""",
                        context=candidate
                    )
                    # Check revised solution
                    revised_match = re.search(r'\b\d{3}\b', revised)
                    if revised_match:
                        validated_solutions.append(revised)
                    else:
                        validated_solutions.append(candidate)  # Keep original if revision didn't yield answer
            else:
                validated_solutions.append(candidate)

        # Step 6: Ensemble final answer from all candidates
        final_answer = await self.ensemble(
            instruction="""Select the best final answer from these candidate solutions:
            - Prioritize solutions that yield an integer between 000 and 999
            - Prefer solutions with clear, step-by-step reasoning
            - Favor solutions that have been computationally verified
            - If multiple valid answers, select the one with strongest justification
            - Extract ONLY the three-digit integer answer (000-999)
            
            Return ONLY the three-digit integer, nothing else.""",
            contexts_list=validated_solutions
        )

        # Step 7: Final extraction and formatting
        # Ensure we have a clean three-digit integer
        final_match = re.search(r'\b\d{3}\b', final_answer)
        if final_match:
            return final_match.group(0)
        else:
            # Fallback: extract any number and format to three digits
            numbers = re.findall(r'\d+', final_answer)
            if numbers:
                return numbers[0].zfill(3)[-3:]  # Pad with zeros and take last 3 digits
            else:
                return "000"  # Ultimate fallback