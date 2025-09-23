# Workflow ID: mbppplus_57_0
# Benchmark: mbppplus
# Data Indices: [143, 324]

import asyncio

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

        # Step 1: Deep problem analysis and classification
        problem_analysis = await self.generate(
            instruction="""Perform a comprehensive analysis of this programming problem. Your analysis must include:
            1. Problem classification: Is this primarily a logical, mathematical, string manipulation, or data structure problem?
            2. Key operations required: What specific operations must be performed? (e.g., filtering, aggregation, transformation)
            3. Edge cases: What edge cases must be handled? (empty inputs, single elements, boundary values, type variations)
            4. Input/output specifications: What are the exact input types and expected output types?
            5. Constraints: Are there any performance, memory, or implementation constraints?
            6. Solution approaches: List 2-3 potential solution strategies with their pros and cons.
            Format your response as a structured JSON-like analysis.""",
            context=""
        )

        # Step 2: Conditional decomposition - only if problem is complex
        decomposition_needed = await self.generate(
            instruction=f"""Based on this analysis:
            {problem_analysis}
            
            Determine if this problem requires decomposition into subproblems. Consider:
            - Does it involve multiple distinct operations?
            - Are there interdependent steps?
            - Would breaking it down improve solution clarity or correctness?
            Respond with 'YES' if decomposition is needed, 'NO' otherwise.""",
            context=problem_analysis
        )

        subproblems = []
        if "YES" in decomposition_needed.upper():
            decomposition_result = await self.decompose(
                instruction="""Break this problem down into the minimal set of interdependent subproblems. For each subproblem:
                - Clearly define what needs to be solved
                - Specify any dependencies on other subproblems
                - Indicate the expected input and output for this subproblem
                Focus on creating independent, testable units where possible.""",
                context=problem_analysis
            )
            subproblems = decomposition_result

        # Step 3: Generate multiple solution approaches in parallel
        solution_approaches = [
            """Generate a solution using functional programming principles (map, filter, reduce, any, all, etc.). 
            Focus on conciseness and leveraging built-in Python functions. Handle edge cases explicitly.""",
            
            """Generate a solution using imperative programming (for loops, while loops, explicit conditionals). 
            Focus on clarity and step-by-step logic. Include detailed comments explaining edge case handling.""",
            
            """Generate a solution using data structure transformations (converting to sets, lists, dictionaries as appropriate). 
            Focus on leveraging Python's data structure capabilities. Consider performance implications."""
        ]

        solution_candidates = await asyncio.gather(
            *[self.generate(
                instruction=f"""Based on the problem analysis:
                {problem_analysis}
                
                {approach}
                
                Generate a complete Python function implementation that:
                - Uses the exact function signature specified in the problem
                - Handles all identified edge cases
                - Includes necessary imports
                - Returns the correct data type
                - Is production-ready and robust
                
                Format your response as ONLY the Python code, nothing else.""",
                context=problem_analysis
            ) for approach in solution_approaches]
        )

        # Step 4: Validate each solution candidate
        validation_tasks = []
        for i, candidate in enumerate(solution_candidates):
            validation_task = self.generate(
                instruction=f"""Critically evaluate this solution candidate:
                {candidate}
                
                Check for:
                1. Correctness: Does it solve the problem as specified?
                2. Edge case handling: Does it handle all edge cases identified in the analysis?
                3. Code quality: Is it clean, readable, and efficient?
                4. Type safety: Does it handle input/output types correctly?
                5. Potential bugs: Are there any logical errors or corner cases it might miss?
                
                Provide a detailed critique with specific suggestions for improvement if needed.""",
                context=candidate
            )
            validation_tasks.append(validation_task)
        
        validations = await asyncio.gather(*validation_tasks)

        # Step 5: Revise solutions based on validation feedback
        revised_solutions = []
        for i, (candidate, validation) in enumerate(zip(solution_candidates, validations)):
            if "error" in validation.lower() or "bug" in validation.lower() or "issue" in validation.lower():
                revised = await self.revise(
                    instruction=f"""Improve this solution based on the following critique:
                    {validation}
                    
                    Specifically:
                    - Fix any identified bugs or logical errors
                    - Improve edge case handling
                    - Enhance code clarity if needed
                    - Ensure type correctness
                    
                    Return ONLY the improved Python code, nothing else.""",
                    context=candidate
                )
                revised_solutions.append(revised)
            else:
                revised_solutions.append(candidate)

        # Step 6: Ensemble - select or synthesize the best solution
        final_solution = await self.ensemble(
            instruction="""Evaluate all solution candidates and select the best one based on:
            1. Correctness and completeness
            2. Code quality and readability
            3. Robustness (edge case handling)
            4. Efficiency
            5. Adherence to Python best practices
            
            If multiple solutions are equally good, synthesize them into a hybrid solution that combines their strengths.
            Return ONLY the final Python code, nothing else.""",
            contexts_list=revised_solutions
        )

        # Step 7: Final meta-validation - have the system critique its own final answer
        final_validation = await self.generate(
            instruction=f"""Perform a final, rigorous validation of this solution:
            {final_solution}
            
            Imagine you are trying to break this code. Consider:
            - What edge cases might still be unhandled?
            - Are there any type coercion issues?
            - Could there be performance bottlenecks?
            - Is the solution unnecessarily complex or could it be simplified?
            - Does it match the exact function signature required?
            
            If you identify any issues, suggest specific improvements. Otherwise, confirm the solution is robust.""",
            context=final_solution
        )

        # Step 8: One final revision if needed
        if "issue" in final_validation.lower() or "improve" in final_validation.lower() or "bug" in final_validation.lower():
            final_solution = await self.revise(
                instruction=f"""Make final improvements based on this validation:
                {final_validation}
                
                Return ONLY the final, improved Python code, nothing else.""",
                context=final_solution
            )

        return final_solution