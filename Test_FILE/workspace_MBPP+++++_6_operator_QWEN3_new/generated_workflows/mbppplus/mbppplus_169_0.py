# Workflow ID: mbppplus_169_0
# Benchmark: mbppplus
# Data Indices: [1, 262]

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
        import re

        # Phase 1: Multi-perspective problem analysis (Parallel Fork)
        problem_analysis_tasks = [
            self.generate(
                instruction="""Categorize this programming problem with extreme precision:
                1. Primary domain: Is it string manipulation, array/list processing, mathematical computation, or data structure algorithm?
                2. Algorithmic pattern: Does it suggest hash maps, sorting, two-pointers, sliding window, recursion, or greedy approach?
                3. Input characteristics: What data types are involved? Are there constraints on size or values?
                4. Output requirements: What exact type must be returned? Are there formatting rules?
                5. Complexity hint: Is efficiency critical (O(n) vs O(n^2))? 
                Output as structured bullet points with clear labels.""",
                context=""
            ),
            self.generate(
                instruction="""Extract all explicit and implicit constraints and edge cases:
                - Empty input scenarios
                - Single element cases
                - Duplicate handling requirements
                - Boundary conditions (min/max values, overflow risks)
                - Type conversion needs
                - Order preservation requirements
                - Performance constraints
                List each with specific examples relevant to this problem.""",
                context=""
            ),
            self.generate(
                instruction="""Hypothesize 2-3 potential solution strategies:
                For each strategy, describe:
                - Core algorithmic approach
                - Data structures needed
                - Time/space complexity
                - Pros and cons for this specific problem
                - Risk of edge case failures
                Format as numbered strategies with detailed analysis.""",
                context=""
            )
        ]
        
        analysis_results = await asyncio.gather(*problem_analysis_tasks)
        category_analysis, constraint_analysis, strategy_analysis = analysis_results

        # Phase 2: Synthesize unified implementation plan (Ensemble)
        implementation_plan = await self.ensemble(
            instruction=f"""Synthesize a comprehensive implementation plan from these analyses:
            CATEGORIZATION: {category_analysis}
            CONSTRAINTS: {constraint_analysis}
            STRATEGIES: {strategy_analysis}
            
            Create a step-by-step blueprint including:
            1. Exact function signature to implement (preserve original name and parameters)
            2. Required preprocessing steps (sorting, deduplication, type conversion)
            3. Core algorithm with loop/recursion structure
            4. Edge case handling protocol for each identified constraint
            5. Return value construction with type enforcement
            6. Efficiency optimization opportunities
            7. Potential failure points and defensive checks
            
            Output as a numbered implementation checklist with concrete, actionable steps.""",
            contexts_list=analysis_results
        )

        # Phase 3: Determine if decomposition is needed
        decomposition_check = await self.generate(
            instruction=f"""Based on this implementation plan:
            {implementation_plan}
            
            Determine if this problem requires explicit decomposition into subproblems.
            Answer only 'YES' or 'NO' followed by brief justification.
            Say 'YES' if: multiple distinct phases, state dependencies, or complex preprocessing needed.
            Say 'NO' if: single-pass algorithm or trivial transformation.""",
            context=implementation_plan
        )

        # Phase 4: Conditional decomposition path
        final_context = implementation_plan
        if "YES" in decomposition_check.upper():
            subproblems = await self.decompose(
                instruction=f"""Decompose this implementation plan into ordered subproblems:
                {implementation_plan}
                
                Each subproblem should be:
                - Atomic and independently solvable
                - Clearly dependent on previous subproblems if needed
                - Focused on a single transformation or computation step
                - Include specific input/output specifications
                
                Prioritize logical flow over minimal subproblem count.""",
                context=implementation_plan
            )
            
            # Summarize decomposition for cleaner context
            decomposition_summary = await self.summarize(
                instruction="""Convert this decomposition into a concise, numbered checklist.
                Each item should be one sentence describing the subproblem's purpose and output.
                Remove implementation details but preserve dependencies and order.""",
                context=str(subproblems)
            )
            final_context = f"IMPLEMENTATION PLAN:\n{implementation_plan}\n\nDECOMPOSITION:\n{decomposition_summary}"

        # Phase 5: Generate initial code solution
        code_solution = await self.programmer(
            instruction=f"""Implement the solution according to this plan:
            {final_context}
            
            CRITICAL REQUIREMENTS:
            - Use EXACT function name and parameters from original problem
            - Handle ALL edge cases identified in constraints
            - Return correct data type (list vs tuple vs string vs number)
            - Include defensive checks for invalid inputs
            - Optimize for clarity first, then efficiency
            - Add minimal comments only for complex logic
            - NO wrapper functions or classes - only the requested function
            - Include necessary imports inside function if needed
            
            Output ONLY the function implementation with imports.""",
            context=final_context,
            max_retries=1
        )

        # Phase 6: Validation and refinement loop (Cascade with Feedback)
        current_solution = code_solution
        for iteration in range(3):  # Max 3 refinement iterations
            validation_feedback = await self.revise(
                instruction=f"""Rigorously validate this code against all edge cases:
                ORIGINAL PLAN: {final_context}
                
                Perform mental execution for:
                1. Empty input cases
                2. Single element inputs
                3. Duplicate-heavy inputs
                4. Boundary value inputs
                5. Type edge cases (None, mixed types if applicable)
                6. Performance stress cases (large inputs)
                
                Check for:
                - Logic errors in loops/conditions
                - Off-by-one errors
                - Type mismatches in returns
                - Unhandled exceptions
                - Efficiency bottlenecks
                
                If any issues found, rewrite the ENTIRE function with corrections.
                If no issues, respond with exactly: 'VALIDATED: [brief confirmation]'
                Maintain original function signature and return type requirements.""",
                context=current_solution
            )
            
            if "VALIDATED" in validation_feedback.upper():
                break
            current_solution = validation_feedback

        # Phase 7: Final solution manifest (Meta-cognition)
        solution_manifest = await self.generate(
            instruction=f"""Create a solution manifest for this final implementation:
            CODE: {current_solution}
            PLAN: {final_context}
            
            Summarize in plain English:
            1. What problem does this solve?
            2. What approach was taken and why?
            3. What edge cases are handled?
            4. What are the time/space complexity?
            5. Any remaining limitations or assumptions?
            
            Then verify: Does this manifest align with the original problem statement?
            If not, suggest one final correction. Otherwise, output 'MANIFEST CONFIRMED'.""",
            context=current_solution
        )

        # Return the validated solution
        return current_solution