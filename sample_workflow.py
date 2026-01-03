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
        Universal workflow for code generation from specifications.
        Uses multi-perspective analysis, parallel solution generation,
        and synthesis to handle any problem in the domain.
        """
        import asyncio
        import re

        # Step 1: Extract core problem components
        extraction_instruction = """
        Extract and structure the following from the problem:
        1. Function name (MUST match ENTRY POINT exactly)
        2. Parameter names and types
        3. Return type
        4. All examples from docstring (format as: input -> expected_output)
        5. Key constraints or special requirements mentioned
        
        Format as JSON with keys: function_name, parameters, return_type, examples, constraints
        Be extremely precise - any error in extraction will cause failure.
        """
        problem_structure = await self.generate(
            instruction=extraction_instruction,
            context=""
        )

        # Step 2: Multi-perspective analysis (parallel)
        analysis_instructions = [
            """
            Analyze from a mathematical/logical perspective:
            - What is the underlying computation or transformation?
            - Are there mathematical formulas or algorithms that apply?
            - What are the boundary conditions and edge cases?
            - How should different data types be handled?
            Focus on precision and completeness.
            """,
            """
            Analyze from an implementation perspective:
            - What Python constructs are most appropriate?
            - Are there built-in functions or standard library modules that could help?
            - What are potential performance considerations?
            - How to handle type conversions or special formatting?
            Focus on practical implementation details.
            """,
            """
            Analyze edge cases and failure modes:
            - What inputs might break a naive implementation?
            - Are there implicit constraints not stated in examples?
            - What are the corner cases for each parameter type?
            - How should errors or unexpected inputs be handled?
            Be exhaustive in considering edge cases.
            """,
            """
            Analyze from a pattern recognition perspective:
            - What patterns emerge from the examples?
            - Is there a general rule that covers all examples?
            - How do the inputs map to outputs systematically?
            - Are there hidden invariants or properties to leverage?
            Focus on deriving the general rule from specific examples.
            """
        ]

        # Run analyses in parallel
        analyses = await asyncio.gather(
            *[self.generate(instruction=instr, context=problem_structure) 
              for instr in analysis_instructions]
        )

        # Step 3: Generate candidate solutions based on analyses
        solution_instructions = [
            f"""
            Generate a complete Python function implementation based on this analysis:
            {analyses[0]}
            
            CRITICAL REQUIREMENTS:
            - Function name MUST exactly match the extracted function name
            - Parameter names and types MUST match specification
            - Return type MUST match specification
            - Code must handle all extracted examples correctly
            - Code must handle edge cases identified in analysis
            - Return ONLY the function code, no explanations
            """,
            f"""
            Generate a complete Python function implementation based on this analysis:
            {analyses[1]}
            
            CRITICAL REQUIREMENTS:
            - Function name MUST exactly match the extracted function name
            - Parameter names and types MUST match specification
            - Return type MUST match specification
            - Code must handle all extracted examples correctly
            - Code must handle edge cases identified in analysis
            - Return ONLY the function code, no explanations
            """,
            f"""
            Generate a complete Python function implementation based on this analysis:
            {analyses[2]}
            
            CRITICAL REQUIREMENTS:
            - Function name MUST exactly match the extracted function name
            - Parameter names and types MUST match specification
            - Return type MUST match specification
            - Code must handle all extracted examples correctly
            - Code must handle edge cases identified in analysis
            - Return ONLY the function code, no explanations
            """,
            f"""
            Generate a complete Python function implementation based on this analysis:
            {analyses[3]}
            
            CRITICAL REQUIREMENTS:
            - Function name MUST exactly match the extracted function name
            - Parameter names and types MUST match specification
            - Return type MUST match specification
            - Code must handle all extracted examples correctly
            - Code must handle edge cases identified in analysis
            - Return ONLY the function code, no explanations
            """
        ]

        # Generate solutions in parallel
        candidate_solutions = await asyncio.gather(
            *[self.generate(instruction=instr, context=problem_structure) 
              for instr in solution_instructions]
        )

        # Step 4: Ensemble - synthesize best solution
        ensemble_instruction = f"""
        You have multiple candidate solutions for the same problem.
        Your task is to synthesize the best possible solution by:
        1. Identifying the strongest aspects of each candidate
        2. Combining them into a single optimal solution
        3. Ensuring all requirements are met:
           - Function name matches exactly
           - Parameters and return type correct
           - Handles all examples from docstring
           - Addresses edge cases from analyses
        4. Making the code clean, efficient, and Pythonic
        
        Problem structure for reference:
        {problem_structure}
        
        Return ONLY the final function code, nothing else.
        """
        
        final_solution = await self.ensemble(
            instruction=ensemble_instruction,
            contexts_list=candidate_solutions
        )

        # Step 5: Final validation and refinement
        refinement_instruction = f"""
        Perform final validation and refinement:
        1. Verify function name EXACTLY matches required entry point
        2. Check that parameter names and types match specification
        3. Ensure return type is correct
        4. Validate against all examples extracted from docstring
        5. Clean up any unnecessary complexity or redundancy
        6. Ensure code is idiomatic Python
        
        Problem structure for reference:
        {problem_structure}
        
        If any issues are found, fix them. Otherwise, return the code unchanged.
        Return ONLY the function code, nothing else.
        """
        
        refined_solution = await self.revise(
            instruction=refinement_instruction,
            context=final_solution
        )

        return refined_solution

