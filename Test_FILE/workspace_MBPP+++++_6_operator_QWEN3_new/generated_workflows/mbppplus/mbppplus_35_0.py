# Workflow ID: mbppplus_35_0
# Benchmark: mbppplus
# Data Indices: [203, 235]

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
        self.programmer = operator.Programmer(self.llm, self.problem_text)
        self.decompose = operator.Decompose(self.llm, self.problem_text)

    async def run_workflow(self):
        """
        Universal workflow for programming problem solving with adaptive strategy selection.
        Handles any problem in the domain by dynamically choosing appropriate solution approaches.
        """
        import asyncio
        import re
        
        # Step 1: Decompose the problem to understand its structure and requirements
        decomposition = await self.decompose(
            instruction="""Break down this programming problem into its fundamental components:
            1. Identify the core task: What exactly needs to be computed or determined?
            2. Analyze input/output: What are the data types and structures involved?
            3. Determine algorithm category: Is this a pattern recognition, mathematical computation, 
               data structure manipulation, or classic algorithm problem?
            4. Identify edge cases: What boundary conditions and special inputs must be handled?
            5. Assess complexity: Is this a simple iteration problem or does it require sophisticated algorithms?
            6. Extract any constraints: Time/space complexity requirements, specific implementation restrictions.
            Return structured decomposition with clear subproblems and dependencies.""",
            context=""
        )
        
        # Step 2: Generate multiple analysis perspectives in parallel
        analysis_tasks = [
            self.generate(
                instruction="""Perform mathematical analysis of the problem:
                - Identify any mathematical patterns, formulas, or theorems that apply
                - Determine if this is a known mathematical problem type
                - Analyze numerical properties and relationships
                - Consider mathematical optimizations or simplifications
                - Identify potential mathematical edge cases (zero, negative numbers, overflow)""",
                context=""
            ),
            self.generate(
                instruction="""Perform algorithmic analysis of the problem:
                - Identify if this matches any classic algorithm patterns (sorting, searching, DP, etc.)
                - Determine appropriate data structures for efficient solution
                - Analyze time/space complexity requirements
                - Consider known algorithmic solutions to similar problems
                - Identify algorithmic edge cases (empty inputs, single elements, worst-case scenarios)""",
                context=""
            ),
            self.generate(
                instruction="""Perform practical implementation analysis:
                - Extract function signature details and parameter meanings
                - Analyze any provided test cases to understand expected behavior
                - Identify implementation pitfalls and common mistakes
                - Consider Python-specific optimizations and idioms
                - Determine return type requirements and data structure expectations""",
                context=""
            )
        ]
        
        # Execute analyses in parallel
        math_analysis, algo_analysis, impl_analysis = await asyncio.gather(*analysis_tasks)
        
        # Step 3: Synthesize analyses to determine optimal approach
        synthesis = await self.ensemble(
            instruction="""Synthesize the three analyses into a unified solution strategy:
            1. Compare and contrast the mathematical, algorithmic, and implementation perspectives
            2. Identify consensus points and any conflicts between analyses
            3. Select the most appropriate solution approach based on problem characteristics
            4. Resolve any contradictions by prioritizing implementation requirements and edge case handling
            5. Create a detailed implementation plan that incorporates insights from all perspectives
            6. Specify exact function signature, parameter handling, and return type requirements
            7. Outline key implementation steps and critical considerations""",
            contexts_list=[math_analysis, algo_analysis, impl_analysis]
        )
        
        # Step 4: Generate edge cases for robustness testing
        edge_cases = await self.generate(
            instruction=f"""Generate comprehensive edge cases based on the problem analysis:
            Using the synthesis: {synthesis}
            
            Create edge cases including:
            - Empty inputs and zero-length collections
            - Single element inputs
            - Boundary values (minimum/maximum, zero, negative numbers)
            - Duplicate elements and special values
            - Pathological cases that might break naive implementations
            - Performance stress tests for large inputs
            - Type consistency tests for different data types
            Format as a structured list with brief explanations of why each case is important.""",
            context=synthesis
        )
        
        # Step 5: Generate initial code solution
        initial_code = await self.programmer(
            instruction=f"""Generate Python code solution based on the synthesis:
            Synthesis: {synthesis}
            
            Requirements:
            - Implement exactly as specified in function signature
            - Handle all identified edge cases from: {edge_cases}
            - Use appropriate data types and structures
            - Include defensive programming for unexpected inputs
            - Optimize for clarity and correctness over premature optimization
            - Follow Python best practices and idioms
            - Ensure return type matches requirements exactly
            - Include minimal necessary imports at top of function
            - Code must be self-contained and ready for testing""",
            context=synthesis
        )
        
        # Step 6: Validate and revise code through iterative refinement
        current_code = initial_code
        max_iterations = 3
        
        for i in range(max_iterations):
            validation = await self.generate(
                instruction=f"""Critically validate the code solution:
                Code: {current_code}
                Edge cases: {edge_cases}
                Synthesis: {synthesis}
                
                Check for:
                1. Correctness: Does it solve the core problem correctly?
                2. Edge case handling: Does it handle all identified edge cases?
                3. Type consistency: Are input/output types handled correctly?
                4. Performance: Is the solution reasonably efficient?
                5. Code quality: Is the code clean, readable, and well-structured?
                6. Common pitfalls: Check for off-by-one errors, empty input handling, etc.
                
                Return detailed validation report with specific issues found (if any).""",
                context=current_code
            )
            
            # If no issues found, break early
            if "no issues" in validation.lower() or "correct" in validation.lower() and "error" not in validation.lower():
                break
                
            # Otherwise, revise the code
            current_code = await self.revise(
                instruction=f"""Revise the code to fix identified issues:
                Current code: {current_code}
                Validation report: {validation}
                Edge cases: {edge_cases}
                
                Specific revision requirements:
                1. Fix all identified correctness issues
                2. Improve edge case handling as specified
                3. Ensure type consistency throughout
                4. Maintain or improve code clarity
                5. Preserve function signature and return type requirements
                6. Add comments for complex logic if needed
                
                Return only the revised code with necessary imports.""",
                context=current_code
            )
        
        # Step 7: Final quality assurance and formatting
        final_code = await self.revise(
            instruction="""Perform final quality assurance and formatting:
            - Ensure code follows PEP 8 guidelines
            - Verify function signature matches exactly what's required
            - Check that all necessary imports are included at the top
            - Remove any debug statements or unnecessary comments
            - Ensure return statements are correct and consistent
            - Verify variable names are clear and meaningful
            - Confirm code is self-contained and ready for production use
            - Return ONLY the final code implementation with imports""",
            context=current_code
        )
        
        return final_code