# Workflow ID: mbppplus_102_0
# Benchmark: mbppplus
# Data Indices: [111, 157, 239]

# --- DO NOT IMPORT HERE ---
class Workflow:
    def __init__(self, config, problem) -> None:
        # --- DO NOT MODIFY THIS SECTION ---
        self.config = config
        self.problem_text = problem
        self.llm = create(config)
        
        self.generate = operator.Generate(self.llm, self.problem_text)
        self.revise = operator.Revise(self.llm, self.problem_text)
        self.summarize = operator.Summarize(self.llm, self.problem_text)
        self.ensemble = operator.Ensemble(self.llm, self.problem_text)

    async def run_workflow(self):
        """
        Universal workflow for programming problem solving domain.
        Adapts to any problem by analyzing requirements then generating optimal solution.
        """
        import asyncio
        import re
        
        # Phase 1: Deep problem analysis
        analysis = await self.generate(
            instruction="""Perform comprehensive analysis of this programming problem:
            
            1. Identify the exact transformation or operation required:
               - Is it filtering, mapping, reducing, counting, or conditional logic?
               - What is the precise rule that must be applied?
            
            2. Analyze data structures:
               - Input type and structure (list, tuple, nested structures, etc.)
               - Output type and structure requirements
               - Any type conversion needed (list to tuple, etc.)
            
            3. Identify critical constraints:
               - Must order be preserved?
               - How should duplicates be handled?
               - Are there special cases (empty inputs, single elements)?
               - Any performance considerations?
            
            4. Extract function signature requirements:
               - Exact function name
               - Parameter names and types
               - Return type specification
            
            5. Anticipate edge cases:
               - Empty inputs
               - Single element cases
               - Boundary values
               - Duplicate handling
               - Type mixing
            
            6. Determine if external imports are needed
            
            Present analysis in structured format with clear sections.""",
            context=""
        )
        
        # Check if problem is extremely simple (like Check_Solution)
        simple_check = await self.generate(
            instruction=f"""Based on this analysis:
            {analysis}
            
            Determine if this problem can be solved with an extremely simple implementation
            (like a single conditional or trivial operation). If yes, provide the complete
            solution now in the required format. If no, respond with "COMPLEX".
            
            Remember: Output ONLY the function implementation if simple, or "COMPLEX" if not.
            Include imports if needed, use exact function name, preserve signature.""",
            context=analysis
        )
        
        if "COMPLEX" not in simple_check and len(simple_check) < 500:  # Simple case
            # Validate simple solution
            validated = await self.revise(
                instruction="""Verify this solution meets all requirements:
                - Correct function name and signature
                - Proper handling of edge cases
                - Correct return type
                - Includes necessary imports
                - No wrapper code or extra text
                If any issues, fix them. Otherwise, return unchanged.""",
                context=simple_check
            )
            return validated
        
        # Phase 2: Generate multiple solution approaches in parallel
        approaches = await asyncio.gather(
            self.generate(
                instruction=f"""Create a DIRECT, straightforward implementation:
                
                Based on this analysis:
                {analysis}
                
                Implement the most obvious, readable solution that directly follows
                the problem requirements. Prioritize clarity over optimization.
                Handle obvious edge cases but don't over-engineer.
                Use the exact function name and signature specified.
                Include any necessary imports at the top.
                Return ONLY the function implementation, no explanations.""",
                context=analysis
            ),
            self.generate(
                instruction=f"""Create an OPTIMIZED, robust implementation:
                
                Based on this analysis:
                {analysis}
                
                Implement the most efficient solution considering:
                - Time/space complexity
                - Edge case handling (empty inputs, duplicates, etc.)
                - Type safety and consistency
                - Potential performance bottlenecks
                Use appropriate data structures and algorithms.
                Include necessary imports.
                Return ONLY the function implementation.""",
                context=analysis
            ),
            self.generate(
                instruction=f"""Create a DEFENSIVE, comprehensive implementation:
                
                Based on this analysis:
                {analysis}
                
                Implement a solution with maximum robustness:
                - Handle all possible edge cases
                - Include input validation if appropriate
                - Use defensive programming practices
                - Consider unexpected input types or values
                - Add comments for complex logic if needed
                Include necessary imports.
                Return ONLY the function implementation.""",
                context=analysis
            )
        )
        
        # Phase 3: Revise each approach for compliance
        revised_approaches = []
        for i, approach in enumerate(approaches):
            revised = await self.revise(
                instruction=f"""Revise this solution for strict compliance:
                
                Requirements:
                1. Use EXACT function name and signature from problem
                2. Return correct data type (list vs tuple vs set)
                3. Handle empty inputs and edge cases
                4. Include necessary imports at top
                5. NO wrapper code, classes, or extra text
                6. Match expected output format exactly
                
                Fix any issues while preserving the core approach.
                Return ONLY the corrected function implementation.""",
                context=approach
            )
            revised_approaches.append(revised)
        
        # Phase 4: Ensemble synthesis - combine best elements
        final_solution = await self.ensemble(
            instruction=f"""Synthesize the best solution from these approaches:
            
            Analysis context:
            {analysis}
            
            Create a hybrid solution that combines:
            - The clarity and simplicity of the direct approach
            - The efficiency and optimization of the optimized approach  
            - The robustness and edge case handling of the defensive approach
            
            CRITICAL REQUIREMENTS:
            - Use EXACT function name and signature
            - Return correct data type
            - Handle ALL edge cases (empty, single element, duplicates)
            - Include necessary imports at top
            - NO extra text, wrapper code, or explanations
            - Code must be production-ready and pass all test cases
            
            Return ONLY the final function implementation.""",
            contexts_list=revised_approaches
        )
        
        # Final validation and cleanup
        validated_solution = await self.revise(
            instruction="""Final validation and cleanup:
            
            Ensure this solution:
            1. Has correct function signature (name, parameters)
            2. Returns appropriate data type
            3. Handles empty inputs and edge cases
            4. Includes necessary imports at top
            5. Contains NO extra text, comments, or wrapper code
            6. Is properly formatted with consistent indentation
            
            If any issues, fix them. Otherwise, return unchanged.
            Return ONLY the function implementation.""",
            context=final_solution
        )
        
        return validated_solution