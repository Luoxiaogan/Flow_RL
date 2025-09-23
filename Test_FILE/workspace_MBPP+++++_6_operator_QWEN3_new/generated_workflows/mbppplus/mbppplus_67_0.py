# Workflow ID: mbppplus_67_0
# Benchmark: mbppplus
# Data Indices: [265, 317]

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
        
        # Step 1: Meta-analysis - Understand problem type and requirements
        problem_analysis = await self.generate(
            instruction="""Perform deep analysis of this programming problem:
            1. Classify problem type: Is it logical, mathematical, algorithmic, or data manipulation?
            2. Identify required output format and data types
            3. List potential edge cases (empty inputs, boundary values, etc.)
            4. Determine if problem requires decomposition into subproblems
            5. Suggest 2-3 possible solution strategies with their trade-offs
            6. Assess complexity level (simple, moderate, complex)
            7. Note any ambiguities or missing information that need clarification
            Provide structured, detailed analysis to guide subsequent steps.""",
            context=""
        )

        # Step 2: Conditional routing based on complexity
        complexity_assessment = await self.generate(
            instruction=f"""Based on this analysis:
            {problem_analysis}
            
            Classify this problem as either:
            - "SIMPLE": Can be solved with direct code implementation (e.g., simple logic, lookups)
            - "MODERATE": Requires careful algorithm design but no decomposition
            - "COMPLEX": Needs decomposition into subproblems or multiple solution approaches
            - "AMBIGUOUS": Has multiple valid interpretations requiring ensemble approach
            
            Respond with ONLY the classification keyword (SIMPLE, MODERATE, COMPLEX, or AMBIGUOUS).""",
            context=problem_analysis
        )

        # Step 3: Parallel strategy generation for ambiguous/complex problems
        if "AMBIGUOUS" in complexity_assessment or "COMPLEX" in complexity_assessment:
            # Generate multiple solution approaches in parallel
            strategy_attempts = await asyncio.gather(
                self.generate(
                    instruction=f"""Based on analysis:
                    {problem_analysis}
                    
                    Develop Solution Approach #1:
                    - Focus on mathematical/algorithmic elegance
                    - Prioritize efficiency and correctness
                    - Include handling of edge cases
                    - Describe step-by-step reasoning""",
                    context=problem_analysis
                ),
                self.generate(
                    instruction=f"""Based on analysis:
                    {problem_analysis}
                    
                    Develop Solution Approach #2:
                    - Focus on simplicity and readability
                    - Use straightforward logic even if less efficient
                    - Include comprehensive error handling
                    - Describe step-by-step reasoning""",
                    context=problem_analysis
                ),
                self.generate(
                    instruction=f"""Based on analysis:
                    {problem_analysis}
                    
                    Develop Solution Approach #3:
                    - Consider alternative interpretations of the problem
                    - Explore unconventional or creative solutions
                    - Identify potential pitfalls and how to avoid them
                    - Describe step-by-step reasoning""",
                    context=problem_analysis
                )
            )
            
            # Ensemble the best elements from all approaches
            synthesized_strategy = await self.ensemble(
                instruction="""Synthesize the best elements from all solution approaches:
                1. Identify the most robust and correct core algorithm
                2. Incorporate the clearest explanations and reasoning
                3. Combine the most comprehensive edge case handling
                4. Resolve any contradictions between approaches
                5. Produce a unified, optimal solution strategy
                The result should be a complete, step-by-step solution plan ready for implementation.""",
                contexts_list=strategy_attempts
            )
            
            final_strategy = synthesized_strategy
        elif "COMPLEX" in complexity_assessment:
            # Decompose into subproblems
            subproblems = await self.decompose(
                instruction=f"""Break down this complex problem into manageable subproblems:
                Based on analysis: {problem_analysis}
                
                Create a hierarchical decomposition where:
                1. Each subproblem is self-contained and solvable independently
                2. Dependencies between subproblems are clearly specified
                3. The decomposition follows a logical progression toward the final solution
                4. Include handling of edge cases at appropriate levels
                5. The final subproblem should integrate all previous results
                
                Return a list of subproblems with IDs and dependencies.""",
                context=problem_analysis
            )
            
            # Solve subproblems in dependency order
            solutions = {}
            for subproblem in subproblems:
                # Wait for dependencies to be solved
                deps = subproblem.get('dependencies', '').split(',') if subproblem.get('dependencies') else []
                deps = [d.strip() for d in deps if d.strip()]
                
                if deps:
                    # Wait for all dependencies to be solved
                    await asyncio.gather(*[asyncio.sleep(0.1) for d in deps if d in solutions])  # Simple dependency wait
                
                # Generate solution for this subproblem
                sub_solution = await self.generate(
                    instruction=f"""Solve this subproblem:
                    {subproblem['description']}
                    
                    Context from problem analysis:
                    {problem_analysis}
                    
                    Previous subproblem solutions:
                    {json.dumps({k: v for k, v in solutions.items() if k in deps}, indent=2) if deps else 'None'}
                    
                    Provide a complete, detailed solution including:
                    - Step-by-step reasoning
                    - Code implementation if applicable
                    - Edge case handling
                    - Verification method""",
                    context=json.dumps(subproblem)
                )
                solutions[subproblem['id']] = sub_solution
            
            # Integrate all subproblem solutions
            final_strategy = await self.generate(
                instruction=f"""Integrate all subproblem solutions into a complete solution:
                Subproblem solutions: {json.dumps(solutions, indent=2)}
                
                Problem analysis: {problem_analysis}
                
                Create a unified solution that:
                1. Combines all subproblem solutions logically
                2. Ensures consistency between components
                3. Provides complete end-to-end implementation
                4. Includes comprehensive error handling and edge cases
                5. Is ready for code implementation""",
                context=json.dumps(solutions)
            )
        else:
            # Simple or moderate problems: direct strategy generation
            final_strategy = await self.generate(
                instruction=f"""Based on analysis:
                {problem_analysis}
                
                Develop a complete solution strategy:
                - Include step-by-step reasoning
                - Specify exact algorithm or approach
                - Detail edge case handling
                - Describe expected output format
                - Provide verification method
                The strategy should be ready for direct code implementation.""",
                context=problem_analysis
            )

        # Step 4: Generate code implementation
        initial_code = await self.programmer(
            instruction=f"""Implement the solution based on this strategy:
            {final_strategy}
            
            Requirements:
            1. Use EXACT function name and signature from problem
            2. Handle all edge cases identified in analysis
            3. Return correct data type (list, tuple, set, etc.)
            4. Include necessary imports
            5. Code must be clean, readable, and efficient
            6. Do NOT include test cases or print statements
            7. Return ONLY the function implementation as specified""",
            context=final_strategy
        )

        # Step 5: Validation and iterative refinement
        validation_result = await self.generate(
            instruction=f"""Validate this code implementation:
            {initial_code}
            
            Against problem requirements:
            {self.problem_text}
            
            Check for:
            1. Correct function signature and name
            2. Proper handling of edge cases
            3. Correct return type and format
            4. Algorithmic correctness
            5. Potential bugs or logical errors
            6. Code style and readability
            
            If any issues found, describe them specifically.
            If no issues, respond with "VALID: Code meets all requirements."""",
            context=initial_code
        )

        current_code = initial_code
        max_iterations = 3
        for i in range(max_iterations):
            if "VALID:" in validation_result and "meets all requirements" in validation_result:
                break
                
            # Revise code based on validation feedback
            current_code = await self.revise(
                instruction=f"""Revise the code based on this validation feedback:
                {validation_result}
                
                Original problem: {self.problem_text}
                Current code: {current_code}
                
                Fix all identified issues while preserving:
                1. Correct function signature
                2. Algorithmic approach
                3. Edge case handling
                4. Code readability
                
                Return ONLY the revised function implementation.""",
                context=current_code
            )
            
            # Re-validate
            validation_result = await self.generate(
                instruction=f"""Re-validate this revised code:
                {current_code}
                
                Against problem requirements and previous feedback:
                {validation_result}
                
                Check if all issues have been resolved.
                If fully valid, respond with "VALID: Code meets all requirements."
                Otherwise, describe remaining issues.""",
                context=current_code
            )

        # Step 6: Final verification and return
        final_verification = await self.generate(
            instruction=f"""Perform final verification of this code:
            {current_code}
            
            Ensure:
            1. Function name and signature exactly match problem requirements
            2. All edge cases are handled
            3. Return type is correct
            4. Code is clean and follows best practices
            5. No unnecessary imports or code
            
            If any final adjustments needed, make them.
            Return ONLY the final function implementation.""",
            context=current_code
        )

        return final_verification