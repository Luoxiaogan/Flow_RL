# Workflow ID: mbppplus_135_0
# Benchmark: mbppplus
# Data Indices: [355, 170]

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
        """
        Universal workflow for programming problem solving with adaptive complexity handling.
        """
        import asyncio
        import re
        import json
        from typing import List, Dict, Any

        # Phase 1: Comprehensive Problem Analysis
        problem_analysis = await self.generate(
            instruction="""Perform deep analysis of this programming problem:
            1. Identify the core task: What transformation or validation is required?
            2. Classify problem type: string manipulation, data structure, algorithm, validation, etc.
            3. Extract key constraints: input types, output format, edge cases to consider
            4. Identify potential failure modes: empty inputs, boundary conditions, type mismatches
            5. Determine if problem requires state tracking, recursion, or simple pattern matching
            6. Note any implicit requirements from test cases (if visible) or problem description
            7. Suggest 2-3 possible solution approaches with their trade-offs
            8. Flag any ambiguous requirements that need clarification
            
            Structure your response with clear section headers for each point above.""",
            context=""
        )

        # Phase 2: Conditional Strategy Selection
        strategy_assessment = await self.generate(
            instruction=f"""Based on this analysis:
            {problem_analysis}
            
            Determine the optimal solution strategy:
            - If problem is simple pattern matching (like string splitting), choose DIRECT_IMPLEMENTATION
            - If problem requires state management (like bracket validation), choose DECOMPOSE_THEN_IMPLEMENT
            - If problem has multiple valid approaches, choose PARALLEL_IMPLEMENTATION
            - If problem is ambiguous, choose CLARIFY_THEN_PROCEED
            
            Also estimate complexity level (1-5) and identify critical edge cases that must be handled.
            
            Respond in JSON format: {{"strategy": "strategy_name", "complexity": number, "critical_edge_cases": ["case1", "case2"]}}""",
            context=problem_analysis
        )

        try:
            strategy_data = json.loads(strategy_assessment)
            strategy = strategy_data.get("strategy", "DIRECT_IMPLEMENTATION")
            complexity = strategy_data.get("complexity", 2)
        except:
            # Fallback if JSON parsing fails
            strategy = "DIRECT_IMPLEMENTATION"
            complexity = 2

        # Phase 3: Adaptive Implementation
        if strategy == "DECOMPOSE_THEN_IMPLEMENT":
            # Break down complex problems
            subproblems = await self.decompose(
                instruction=f"""Decompose this problem into atomic subproblems:
                - Each subproblem should be independently solvable
                - Include dependencies between subproblems
                - Focus on state management and edge case handling
                - Ensure subproblems cover all critical edge cases identified: {strategy_data.get('critical_edge_cases', [])}
                
                Problem context: {problem_analysis}""",
                context=problem_analysis
            )
            
            # Generate implementation plan
            implementation_plan = await self.generate(
                instruction=f"""Create detailed implementation plan based on subproblems:
                Subproblems: {json.dumps(subproblems)}
                
                For each subproblem, specify:
                1. Exact code structure needed
                2. Variables and data structures required
                3. Edge case handling strategy
                4. Integration points with other subproblems
                
                Provide complete pseudocode outline.""",
                context=json.dumps(subproblems)
            )
            
            # Generate code with specific focus on edge cases
            initial_code = await self.programmer(
                instruction=f"""Implement solution following this plan:
                {implementation_plan}
                
                CRITICAL REQUIREMENTS:
                - Handle all edge cases: {strategy_data.get('critical_edge_cases', [])}
                - Use exact function signature from problem
                - Include necessary imports inside function if needed
                - Return appropriate data types as specified
                - Write defensive code that handles unexpected inputs gracefully
                - Prioritize correctness over cleverness
                
                Generate ONLY the function implementation with exact signature.""",
                context=implementation_plan
            )
            
        elif strategy == "PARALLEL_IMPLEMENTATION":
            # Generate multiple approaches in parallel
            approaches = [
                "Implement using iterative approach with explicit state tracking",
                "Implement using recursive approach with helper functions",
                "Implement using built-in Python features and libraries for maximum simplicity"
            ]
            
            parallel_implementations = await asyncio.gather(
                *[self.programmer(
                    instruction=f"""{approach}
                    
                    CRITICAL REQUIREMENTS:
                    - Handle all edge cases: {strategy_data.get('critical_edge_cases', [])}
                    - Use exact function signature from problem
                    - Include necessary imports inside function if needed
                    - Return appropriate data types as specified
                    - Write defensive code that handles unexpected inputs gracefully
                    
                    Generate ONLY the function implementation with exact signature.""",
                    context=problem_analysis
                ) for approach in approaches]
            )
            
            # Select best implementation
            initial_code = await self.ensemble(
                instruction=f"""Select the best implementation based on:
                1. Correctness and edge case handling
                2. Readability and maintainability
                3. Efficiency and simplicity
                4. Adherence to problem requirements
                
                Problem context: {problem_analysis}
                Critical edge cases: {strategy_data.get('critical_edge_cases', [])}
                
                Choose the implementation that best balances these factors.""",
                contexts_list=parallel_implementations
            )
            
        else:  # DIRECT_IMPLEMENTATION or fallback
            initial_code = await self.programmer(
                instruction=f"""Implement solution directly:
                
                Problem analysis: {problem_analysis}
                Critical edge cases to handle: {strategy_data.get('critical_edge_cases', [])}
                
                CRITICAL REQUIREMENTS:
                - Handle all identified edge cases
                - Use exact function signature from problem
                - Include necessary imports inside function if needed
                - Return appropriate data types as specified
                - Write defensive code that handles unexpected inputs gracefully
                - Keep implementation simple and readable
                
                Generate ONLY the function implementation with exact signature.""",
                context=problem_analysis
            )

        # Phase 4: Robustness Refinement
        refined_code = await self.revise(
            instruction=f"""Critically review this implementation for robustness:
            {initial_code}
            
            Focus areas:
            1. Edge case coverage: Verify handling of empty inputs, single elements, boundary conditions
            2. Type safety: Ensure proper type handling and conversions
            3. Error prevention: Add guards for unexpected inputs
            4. Code clarity: Improve variable names and add minimal comments if needed
            5. Efficiency: Remove unnecessary operations while maintaining correctness
            
            Problem context: {problem_analysis}
            Critical edge cases: {strategy_data.get('critical_edge_cases', [])}
            
            Return ONLY the improved implementation with exact function signature.""",
            context=initial_code
        )

        # Phase 5: Final Validation (if complexity warrants it)
        if complexity >= 3:
            validation_check = await self.generate(
                instruction=f"""Perform final validation of this implementation:
                {refined_code}
                
                Check against:
                1. All critical edge cases: {strategy_data.get('critical_edge_cases', [])}
                2. Problem requirements from original analysis
                3. Potential off-by-one errors or logical gaps
                4. Return type consistency
                
                If any issues found, specify exactly what needs fixing.
                If no issues, respond with "VALIDATED". Otherwise, list specific fixes needed.""",
                context=refined_code
            )
            
            if "VALIDATED" not in validation_check.upper():
                # One final revision if issues found
                final_code = await self.revise(
                    instruction=f"""Fix these specific issues:
                    {validation_check}
                    
                    Implementation to fix:
                    {refined_code}
                    
                    Return ONLY the corrected implementation with exact function signature.""",
                    context=refined_code
                )
                return final_code
        
        return refined_code