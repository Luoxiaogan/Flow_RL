# Workflow ID: mbppplus_171_0
# Benchmark: mbppplus
# Data Indices: [370, 13]

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

        # Step 1: Semantic Analysis - Understand problem type, inputs, outputs, edge cases
        analysis = await self.generate(
            instruction="""Perform deep semantic analysis of this programming problem. Identify:
            1. Problem category (e.g., dynamic programming, greedy, math, string, list/tuple operations)
            2. Input types and structures (e.g., integers, lists of tuples, strings)
            3. Expected output type and format
            4. Algorithmic patterns (e.g., recursion, iteration, memoization, aggregation)
            5. Key constraints and edge cases (empty inputs, zeros, negatives, boundaries)
            6. Similar classic problems (e.g., knapsack, Fibonacci, cumulative sum)
            7. Suggested solution strategy (brute force, optimized, mathematical)
            Provide structured, detailed analysis to guide subsequent steps.""",
            context=""
        )

        # Step 2: Confidence & Complexity Assessment
        complexity = await self.generate(
            instruction=f"""Based on the analysis:
            {analysis}
            
            Classify problem complexity and confidence:
            - Complexity: "trivial", "moderate", "complex"
            - Requires decomposition: "yes" or "no"
            - Multiple valid approaches: "yes" or "no"
            - High risk of edge-case failures: "yes" or "no"
            
            Also, extract the exact function signature that must be implemented.
            Return in JSON-like format for easy parsing.""",
            context=analysis
        )

        # Step 3: Adaptive Strategy Branching
        if "trivial" in complexity.lower() and "no" in complexity.lower():
            # Simple problems: direct code generation with edge-case emphasis
            solution = await self.programmer(
                instruction=f"""Implement the function with this exact signature. 
                Problem analysis: {analysis}
                Requirements:
                - Handle all edge cases (empty, zero, negative, boundary)
                - Return correct data type
                - No extra output - ONLY the function
                - Include necessary imports inside function if needed
                - Optimize for clarity and correctness, not performance""",
                context=analysis,
                max_retries=1
            )
        else:
            # Complex problems: parallel approach generation + decomposition
            approach_tasks = [
                self.generate(
                    instruction=f"""Solve using {approach} approach:
                    Problem: {self.problem_text}
                    Analysis: {analysis}
                    Requirements:
                    - Handle edge cases explicitly
                    - Return correct data type
                    - Include necessary imports
                    - Explain key logic steps in comments
                    """,
                    context=""
                ) for approach in ["dynamic programming", "mathematical formula", "iterative optimization"]
            ]
            
            # Generate multiple solution approaches in parallel
            approaches = await asyncio.gather(*approach_tasks)
            
            # Decompose problem structure for complex cases
            decomposition = await self.decompose(
                instruction=f"""Break down this problem into subproblems with dependencies:
                Analysis: {analysis}
                Requirements:
                - Identify atomic subproblems
                - Specify dependencies between them
                - Include edge case handling as separate subproblem if needed
                - Output in structured format with id, description, dependencies""",
                context=analysis
            )
            
            # Generate code for each subproblem in sequence based on dependencies
            subproblem_solutions = {}
            for subproblem in sorted(decomposition, key=lambda x: len(x.get('dependencies', '').split(','))):
                deps = subproblem.get('dependencies', '').split(',') if subproblem.get('dependencies') else []
                dep_context = "\n".join([subproblem_solutions.get(dep_id.strip(), "") for dep_id in deps if dep_id.strip() in subproblem_solutions])
                
                sub_solution = await self.programmer(
                    instruction=f"""Implement subproblem: {subproblem['description']}
                    Problem context: {analysis}
                    Dependencies: {dep_context}
                    Requirements:
                    - Handle edge cases
                    - Return correct type
                    - Integrate with dependent subproblems
                    - ONLY output the code for this subproblem""",
                    context=dep_context,
                    max_retries=2
                )
                subproblem_solutions[subproblem['id']] = sub_solution
            
            # Combine subproblem solutions into final answer
            combined_context = "\n\n".join([f"Subproblem {k}: {v}" for k, v in subproblem_solutions.items()])
            
            solution = await self.programmer(
                instruction=f"""Combine these subproblem solutions into final function:
                {combined_context}
                Requirements:
                - Maintain exact function signature
                - Handle all edge cases
                - Return correct data type
                - ONLY output the final function, no explanations
                - Include necessary imports inside function""",
                context=combined_context,
                max_retries=1
            )

        # Step 4: Validation and Revision Loop (up to 3 iterations)
        final_solution = solution
        for attempt in range(3):
            validation = await self.generate(
                instruction=f"""Critically validate this code:
                {final_solution}
                Against problem: {self.problem_text}
                Check for:
                - Correct function signature
                - Edge case handling (empty, zero, negative, boundary)
                - Return type correctness
                - Logical errors or off-by-one mistakes
                - Efficiency issues
                If perfect, respond "VALID". Otherwise, describe exact fixes needed.""",
                context=final_solution
            )
            
            if "VALID" in validation.upper():
                break
            else:
                final_solution = await self.revise(
                    instruction=f"""Fix the code based on this validation feedback:
                    {validation}
                    Requirements:
                    - Preserve exact function signature
                    - Handle all edge cases
                    - Return correct data type
                    - ONLY output the corrected function, no explanations
                    - Include necessary imports inside function""",
                    context=final_solution
                )
        else:
            # If still not validated, use ensemble of original and revised versions
            ensemble_result = await self.ensemble(
                instruction="""Select the most correct and robust solution from these candidates.
                Prioritize: edge-case handling, signature correctness, logical soundness.
                Return ONLY the selected function implementation, nothing else.""",
                contexts_list=[solution, final_solution]
            )
            final_solution = ensemble_result

        # Step 5: Final Sanitization - Ensure output matches exact requirements
        sanitized = await self.revise(
            instruction="""Ensure this code meets ALL requirements:
            - ONLY the function implementation (no markdown, no explanations)
            - Exact function signature from problem
            - All necessary imports inside function body
            - No extra output or print statements
            - Handles edge cases (empty, zero, negative, boundary)
            - Returns correct data type
            If any requirement violated, fix it. Output ONLY the function.""",
            context=final_solution
        )

        return sanitized