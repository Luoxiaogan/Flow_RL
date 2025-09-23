# Workflow ID: limr_51_0
# Benchmark: limr
# Data Indices: [196, 117]

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

        # PHASE 1: PROBLEM DISCOVERY & CLASSIFICATION
        problem_analysis = await self.generate(
            instruction="""Perform deep structural analysis of this mathematical problem. Identify:
            1. Primary mathematical domain (combinatorics, geometry, algebra, number theory, etc.)
            2. Key variables, constraints, and relationships
            3. Required output format and precision (must be integer 000-999)
            4. Potential solution strategies (analytical, computational, geometric, etc.)
            5. Any hidden symmetries, invariants, or optimization opportunities
            6. Edge cases or special conditions that might affect the solution
            Present your analysis in a structured, detailed format that can guide subsequent solution steps.""",
            context=""
        )

        # PHASE 2: STRATEGIC DECOMPOSITION
        decomposition = await self.decompose(
            instruction="""Break this problem into minimal, logically independent subproblems. For each:
            - Define the exact mathematical task
            - Specify required inputs and expected outputs
            - Identify dependencies on other subproblems
            - Suggest optimal solution method (analytical, computational, geometric, etc.)
            Prioritize subproblems that can be solved in parallel or that unlock subsequent steps.""",
            context=problem_analysis
        )

        # PHASE 3: PARALLEL SOLUTION GENERATION
        # Generate multiple solution approaches based on decomposition
        solution_tasks = []
        for i, subproblem in enumerate(decomposition):
            task = self.generate(
                instruction=f"""Solve subproblem {subproblem['id']}:
                {subproblem['description']}
                
                Context from problem analysis:
                {problem_analysis}
                
                Guidelines:
                - Use the suggested solution method unless a better approach is evident
                - Show all mathematical steps clearly
                - Verify intermediate results for consistency
                - If computational solution is needed, prepare specifications for programmer""",
                context=problem_analysis
            )
            solution_tasks.append(task)
        
        # Execute solution tasks in parallel
        raw_solutions = await asyncio.gather(*solution_tasks)

        # PHASE 4: COMPUTATIONAL VERIFICATION (if needed)
        # Check if any solution requires computational verification
        computational_checks = []
        for i, solution in enumerate(raw_solutions):
            needs_computation = await self.generate(
                instruction=f"""Determine if solution {i+1} requires computational verification:
                - Does it involve large numbers, combinatorial explosion, or precision-sensitive calculations?
                - Would code execution increase confidence in the result?
                - Is there a risk of manual calculation error?
                
                Solution to evaluate:
                {solution}
                
                Respond with 'YES' or 'NO' only.""",
                context=solution
            )
            
            if "YES" in needs_computation.upper():
                code_spec = await self.generate(
                    instruction=f"""Generate precise specifications for a Python program to verify:
                    {solution}
                    
                    Include:
                    - Required inputs and their sources
                    - Expected outputs and validation criteria
                    - Any mathematical libraries or functions needed
                    - Edge case handling requirements""",
                    context=solution
                )
                
                computational_result = await self.programmer(
                    instruction=f"""Implement and execute code to verify the mathematical solution:
                    {code_spec}
                    
                    Ensure:
                    - Code is mathematically rigorous
                    - All edge cases are handled
                    - Result is precise and matches required format
                    - Output includes both code and result""",
                    context=code_spec
                )
                computational_checks.append(computational_result)
            else:
                computational_checks.append(solution)  # Use original if no computation needed

        # PHASE 5: SOLUTION SYNTHESIS & VALIDATION
        synthesized_solution = await self.ensemble(
            instruction="""Synthesize the most accurate and complete solution from all available approaches:
            - Resolve any contradictions between parallel solutions
            - Combine complementary insights from different approaches
            - Ensure mathematical rigor and logical consistency
            - Verify that final answer is an integer between 000 and 999
            - Format final answer as exactly three digits (e.g., 042, not 42)
            
            Prioritize solutions that:
            1. Are mathematically elegant and efficient
            2. Have been computationally verified
            3. Align with problem constraints and edge cases
            4. Demonstrate clear, step-by-step reasoning""",
            contexts_list=computational_checks
        )

        # PHASE 6: FINAL VALIDATION & REFINEMENT
        final_answer = await self.revise(
            instruction="""Perform final validation and refinement:
            1. Verify that the answer is an integer between 000 and 999
            2. Check that all problem constraints are satisfied
            3. Ensure no calculation errors in final steps
            4. Format answer as exactly three digits (zero-padded if necessary)
            5. Remove any explanatory text - output ONLY the three-digit number
            
            If any issues are found, correct them and output only the final three-digit number.
            Example valid outputs: "042", "177", "999" """,
            context=synthesized_solution
        )

        # Extract just the three-digit number using regex to ensure format
        match = re.search(r'\b\d{3}\b', final_answer)
        if match:
            return match.group(0)
        else:
            # Fallback: try to extract any number and format to three digits
            numbers = re.findall(r'\d+', final_answer)
            if numbers:
                num = int(numbers[0]) % 1000  # Ensure in range
                return f"{num:03d}"
            else:
                return "000"  # Ultimate fallback