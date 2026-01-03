# Workflow ID: mbppplus_81_0
# Benchmark: mbppplus
# Data Indices: [137, 76]

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
        Universal workflow for programming problem solving that handles any problem in the domain.
        Uses hierarchical decomposition, parallel execution, and iterative refinement.
        """
        import asyncio
        import re
        
        # Step 1: Decompose the problem into essential components
        # This creates a universal framework for any programming problem
        decomposition = await self.decompose(
            instruction="""Systematically decompose this programming problem into its essential components. 
            Identify these universal subproblems that apply to ANY programming task:
            1. INPUT VALIDATION: What are the expected input types, ranges, and constraints? What edge cases must be handled?
            2. CORE LOGIC: What is the main algorithmic operation or calculation required?
            3. EDGE CASE HANDLING: What special cases (empty inputs, boundary values, invalid inputs) need explicit handling?
            4. OUTPUT SPECIFICATION: What is the exact return type and format required?
            5. ERROR HANDLING: How should unexpected inputs or conditions be managed?
            
            For each subproblem, provide a clear, actionable description that can be implemented as code.
            Consider examples: For geometric_sum, edge cases include n<0; for validity_triangle, it's ensuring sum=180.
            Format each subproblem with a clear ID and description that can be processed independently.""",
            context=""
        )
        
        # Step 2: Process subproblems in parallel
        # This creates efficiency while maintaining thoroughness
        subproblem_tasks = []
        for subproblem in decomposition:
            # Dynamically construct instruction based on subproblem type
            if "INPUT VALIDATION" in subproblem['description'].upper():
                instruction = f"""Implement input validation logic for this programming problem.
                Problem context: {self.problem_text}
                Subproblem: {subproblem['description']}
                
                Requirements:
                - Check for expected data types
                - Validate input ranges and constraints
                - Return appropriate values for invalid inputs
                - Handle edge cases like None, empty collections, or out-of-range values
                - Keep code minimal and focused on validation only
                - Use clear, descriptive variable names
                """
            elif "CORE LOGIC" in subproblem['description'].upper():
                instruction = f"""Implement the core algorithmic logic for this programming problem.
                Problem context: {self.problem_text}
                Subproblem: {subproblem['description']}
                
                Requirements:
                - Focus only on the main calculation or operation
                - Assume inputs have been validated
                - Use efficient algorithms appropriate for the task
                - Include clear comments explaining the approach
                - Handle any mathematical operations with precision
                - Return the exact data type specified in the problem
                """
            elif "EDGE CASE" in subproblem['description'].upper():
                instruction = f"""Implement edge case handling for this programming problem.
                Problem context: {self.problem_text}
                Subproblem: {subproblem['description']}
                
                Requirements:
                - Handle all identified edge cases explicitly
                - Consider: empty inputs, single elements, boundary values, duplicates
                - Return appropriate values for each edge case
                - Ensure graceful degradation for unexpected inputs
                - Document each edge case with a comment
                """
            elif "OUTPUT" in subproblem['description'].upper():
                instruction = f"""Implement output formatting and type handling for this programming problem.
                Problem context: {self.problem_text}
                Subproblem: {subproblem['description']}
                
                Requirements:
                - Ensure return type matches exactly what's specified
                - Convert between data types if necessary (list vs tuple vs set)
                - Format output precisely as required
                - Include any necessary type conversions or formatting
                - Verify output against problem specifications
                """
            else:  # Default for any other subproblem type
                instruction = f"""Implement this component of the programming problem.
                Problem context: {self.problem_text}
                Subproblem: {subproblem['description']}
                
                Requirements:
                - Focus on the specific task described
                - Keep implementation clean and efficient
                - Use appropriate Python idioms and best practices
                - Include clear, concise comments
                - Return values in the expected format
                """
            
            # Add to parallel execution queue
            subproblem_tasks.append(
                self.programmer(
                    instruction=instruction,
                    context=subproblem['description'],
                    max_retries=3
                )
            )
        
        # Execute all subproblems in parallel
        subproblem_results = await asyncio.gather(*subproblem_tasks)
        
        # Step 3: Ensemble - Synthesize subproblem solutions into complete solution
        complete_solution = await self.ensemble(
            instruction="""Synthesize these subproblem solutions into a complete, cohesive function implementation.
            Requirements:
            1. INTEGRATE COMPONENTS: Combine the input validation, core logic, edge case handling, and output formatting into one function
            2. MAINTAIN CONSISTENCY: Use consistent variable names and coding style throughout
            3. PRESERVE STRUCTURE: Follow the exact function signature specified in the problem
            4. HANDLE DEPENDENCIES: Ensure components are executed in the correct order (validation before core logic, etc.)
            5. OPTIMIZE FLOW: Remove any redundant code or unnecessary steps
            6. FORMAT OUTPUT: Return ONLY the function implementation with necessary imports, no additional text or wrapping
            7. VERIFY REQUIREMENTS: Double-check that all problem requirements are met, including edge cases and return types
            
            The final output should be ONLY the Python function code, ready for execution, with the exact function name specified in the problem.
            Include any necessary imports at the top of the function.
            Do NOT include any explanatory text, markdown, or additional wrapping.""",
            contexts_list=subproblem_results
        )
        
        # Step 4: Revise - Final quality check and refinement
        final_solution = await self.revise(
            instruction="""Perform a comprehensive quality review and refinement of this programming solution.
            Check for these critical aspects:
            1. EDGE CASE COMPLETENESS: Have all possible edge cases been handled? (empty inputs, None, boundary values, invalid types)
            2. TYPE CONSISTENCY: Does the return type exactly match what's specified in the problem? (list vs tuple vs set)
            3. ERROR HANDLING: Is the code robust against unexpected inputs? Does it fail gracefully?
            4. EFFICIENCY: Is the solution reasonably efficient for the problem size? Are there obvious optimizations?
            5. READABILITY: Is the code clean, well-commented, and using descriptive variable names?
            6. REQUIREMENT COMPLIANCE: Does the solution exactly match the problem specification?
            7. FORMAT COMPLIANCE: Is the output ONLY the function implementation with necessary imports? No additional text?
            
            Make any necessary improvements to address issues found in the review.
            The output must be ONLY the refined Python function code, ready for execution.
            Preserve the exact function signature and return type specified in the problem.""",
            context=complete_solution
        )
        
        return final_solution