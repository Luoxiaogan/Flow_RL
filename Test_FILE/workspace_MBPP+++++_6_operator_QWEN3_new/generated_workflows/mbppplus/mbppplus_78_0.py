# Workflow ID: mbppplus_78_0
# Benchmark: mbppplus
# Data Indices: [15, 168]

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
        
        # Phase 1: Problem Decomposition and Understanding
        decomposition_instruction = """
        Analyze the programming problem and decompose it into these essential components:
        1. INPUT SPECIFICATION: What are the exact input parameters? What types are they? 
        2. OUTPUT REQUIREMENT: What should the function return? What type and format?
        3. CORE OPERATION: What is the fundamental algorithmic or logical operation needed?
        4. EDGE CASES: What boundary conditions must be handled? (empty inputs, single elements, etc.)
        5. CONSTRAINTS: Any specific requirements about order preservation, duplicates, performance, etc.
        6. EXAMPLE ANALYSIS: How do the provided test cases illustrate the expected behavior?
        
        Format your response as a structured JSON with keys: input_spec, output_requirement, core_operation, edge_cases, constraints, example_analysis
        """
        
        decomposition = await self.generate(
            instruction=decomposition_instruction,
            context=""
        )
        
        # Phase 2: Parallel Analysis Streams
        # Stream 1: Generate initial solution candidate
        solution_candidate = await self.generate(
            instruction=f"""
            Based on this problem decomposition:
            {decomposition}
            
            Generate a Python function that solves the problem. Pay special attention to:
            - Matching the exact function signature
            - Handling all identified edge cases
            - Returning the correct data type
            - Following Python best practices
            
            Include the complete function implementation with any necessary imports.
            """,
            context=decomposition
        )
        
        # Stream 2: Extract precise type and format requirements
        type_analysis = await self.generate(
            instruction=f"""
            From the problem decomposition:
            {decomposition}
            
            Extract EXACT type requirements:
            - What input types are expected? (list, tuple, set, etc.)
            - What output type is required? (must match exactly)
            - Any specific ordering requirements?
            - How should duplicates be handled?
            
            Be extremely precise - these requirements will be used to validate the solution.
            """,
            context=decomposition
        )
        
        # Stream 3: Generate comprehensive edge case tests
        edge_cases = await self.generate(
            instruction=f"""
            Based on the edge cases identified in the decomposition:
            {decomposition}
            
            Generate a comprehensive set of test cases that cover:
            - Normal cases (as shown in examples)
            - Boundary cases (empty inputs, single elements)
            - Error cases (if any specified)
            - Performance edge cases (large inputs, if relevant)
            
            Format as Python assert statements that could be used to test the solution.
            """,
            context=decomposition
        )
        
        # Phase 3: Solution Validation and Refinement
        validation_instruction = f"""
        Validate this solution candidate against the requirements:
        
        SOLUTION CANDIDATE:
        {solution_candidate}
        
        TYPE REQUIREMENTS:
        {type_analysis}
        
        EDGE CASES:
        {edge_cases}
        
        Check for:
        1. Does the function signature exactly match what's required?
        2. Does it handle all specified edge cases?
        3. Does it return the correct data type?
        4. Are there any logical errors or inefficiencies?
        5. Does it follow Python best practices?
        
        If any issues are found, provide specific, actionable feedback for improvement.
        If no issues are found, respond with "VALIDATED: Solution meets all requirements."
        """
        
        validation = await self.generate(
            instruction=validation_instruction,
            context=solution_candidate
        )
        
        # Phase 4: Conditional Refinement Loop
        current_solution = solution_candidate
        max_iterations = 3
        iteration = 0
        
        while iteration < max_iterations and "VALIDATED" not in validation:
            iteration += 1
            
            # Revise solution based on validation feedback
            current_solution = await self.revise(
                instruction=f"""
                Revise the solution based on this feedback:
                {validation}
                
                Specific requirements to address:
                - Fix any type mismatches
                - Handle all edge cases identified
                - Correct any logical errors
                - Improve code quality if needed
                
                Maintain the exact function signature and return type.
                """,
                context=current_solution
            )
            
            # Re-validate
            validation = await self.generate(
                instruction=validation_instruction.replace(solution_candidate, current_solution),
                context=current_solution
            )
        
        # Phase 5: Generate Alternative Solutions and Ensemble
        alternative_solutions = await asyncio.gather(
            self.generate(
                instruction=f"""
                Generate an alternative solution to the same problem using a different approach.
                Consider: different algorithms, data structures, or implementation styles.
                Still must meet all requirements from decomposition.
                """,
                context=decomposition
            ),
            self.generate(
                instruction=f"""
                Generate a solution focused specifically on edge case robustness.
                Prioritize handling all edge cases over elegance or performance.
                """,
                context=decomposition
            ),
            self.generate(
                instruction=f"""
                Generate the most concise, elegant solution possible.
                Focus on code clarity and Pythonic style while meeting requirements.
                """,
                context=decomposition
            )
        )
        
        # Add the validated solution to alternatives
        all_solutions = [current_solution] + list(alternative_solutions)
        
        # Ensemble: Select or synthesize the best solution
        final_solution = await self.ensemble(
            instruction="""
            Evaluate all candidate solutions and select the best one based on:
            1. Correctness (must handle all edge cases and requirements)
            2. Code quality (readability, Pythonic style)
            3. Robustness (handles edge cases gracefully)
            4. Efficiency (reasonable performance)
            
            If one solution is clearly superior, select it.
            If multiple solutions have complementary strengths, synthesize a new solution combining the best aspects.
            
            Return ONLY the final Python function implementation with necessary imports.
            """,
            contexts_list=all_solutions
        )
        
        # Phase 6: Final Verification
        final_verification = await self.generate(
            instruction=f"""
            Perform final verification of this solution:
            {final_solution}
            
            Double-check:
            - Function signature matches exactly
            - Return type is correct
            - All edge cases are handled
            - No syntax errors
            - Follows all requirements from original decomposition
            
            If any issues remain, note them specifically.
            Otherwise, respond with "FINAL VERIFICATION PASSED".
            """,
            context=final_solution
        )
        
        # One last revision if needed
        if "FINAL VERIFICATION PASSED" not in final_verification:
            final_solution = await self.revise(
                instruction=f"""
                Make final corrections based on this verification feedback:
                {final_verification}
                
                This is the last chance to fix any remaining issues.
                Ensure perfect compliance with all requirements.
                """,
                context=final_solution
            )
        
        return final_solution