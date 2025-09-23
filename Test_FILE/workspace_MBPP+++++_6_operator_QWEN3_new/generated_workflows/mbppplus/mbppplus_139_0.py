# Workflow ID: mbppplus_139_0
# Benchmark: mbppplus
# Data Indices: [125, 281]

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

        # Phase 1: Multi-perspective problem analysis (Diamond Pattern)
        analysis_tasks = [
            self.generate(
                instruction="""Adopt a MATHEMATICAL lens. Analyze the problem for:
                - Numerical patterns, sequences, or transformations
                - Algebraic relationships between inputs and outputs
                - Arithmetic, geometric, or logical operations involved
                - Dimensional analysis (units, scaling, proportions)
                - Whether solution requires iteration, recursion, or direct computation
                Structure your response as: [Mathematical Analysis]: <detailed breakdown>""",
                context=""
            ),
            self.generate(
                instruction="""Adopt a DATA STRUCTURE lens. Analyze the problem for:
                - Input/output data types (list, tuple, string, set, etc.)
                - Structural transformations (filtering, mapping, reducing, zipping)
                - Order preservation requirements
                - Handling of duplicates, emptiness, or boundary cases
                - Whether problem is element-wise, aggregate, or relational
                Structure your response as: [Data Structure Analysis]: <detailed breakdown>""",
                context=""
            ),
            self.generate(
                instruction="""Adopt an EDGE CASE & CONSTRAINT lens. Analyze the problem for:
                - Explicit and implicit constraints
                - Boundary conditions (empty inputs, single elements, extremes)
                - Type safety requirements
                - Error conditions or invalid inputs to handle
                - Performance or efficiency constraints
                Structure your response as: [Edge Case Analysis]: <detailed breakdown>""",
                context=""
            )
        ]
        
        analysis_results = await asyncio.gather(*analysis_tasks)
        
        # Phase 2: Synthesize analyses into unified problem profile
        problem_profile = await self.ensemble(
            instruction="""Synthesize the three analytical perspectives into a unified problem profile. Include:
            1. Problem type classification (e.g., "element-wise tuple transformation", "geometric calculation")
            2. Required input/output types and structures
            3. Core algorithmic pattern (e.g., "sliding window", "pairwise operation", "direct formula")
            4. Critical edge cases to handle
            5. Confidence level in classification (high/medium/low)
            Format as structured JSON-like output with clear section headers.""",
            contexts_list=analysis_results
        )

        # Phase 3: Conditional routing based on problem type
        # Extract classification for branching
        classification_analysis = await self.generate(
            instruction="""From the problem profile, extract ONLY the primary problem type classification. 
            Respond with exactly one of: "algorithmic_computation", "data_transformation", "logical_validation", "multi_step_decomposition"
            If uncertain, default to "algorithmic_computation".""",
            context=problem_profile
        )
        
        solution = None
        attempt_count = 0
        max_attempts = 3
        
        while attempt_count < max_attempts:
            attempt_count += 1
            
            if "algorithmic_computation" in classification_analysis or "data_transformation" in classification_analysis:
                # Route to Programmer with rich context
                programmer_instruction = f"""Generate Python code to solve this problem based on the following specification:
                
                PROBLEM PROFILE:
                {problem_profile}
                
                REQUIREMENTS:
                - Match exact function signature from problem
                - Handle all edge cases identified in profile
                - Return correct data type (tuple, list, etc.) as specified
                - Include necessary imports within function if needed
                - Code must be self-contained and immediately executable
                - Prioritize clarity and correctness over premature optimization
                
                OUTPUT FORMAT:
                Return ONLY the Python function implementation with no additional text, markdown, or explanation.
                Begin with any necessary imports, then the function definition."""
                
                solution = await self.programmer(
                    instruction=programmer_instruction,
                    context=problem_profile,
                    max_retries=1
                )
                
            elif "logical_validation" in classification_analysis:
                # Generate natural language solution then convert to code
                nl_solution = await self.generate(
                    instruction=f"""Generate a step-by-step natural language solution to this problem:
                    {problem_profile}
                    
                    Include:
                    - Precise algorithmic steps
                    - Handling of edge cases
                    - Expected input/output transformations
                    - Any mathematical formulas or logical rules applied""",
                    context=problem_profile
                )
                
                solution = await self.programmer(
                    instruction=f"""Convert this natural language solution into Python code:
                    {nl_solution}
                    
                    Follow all requirements from problem profile. Return ONLY the function implementation.""",
                    context=nl_solution,
                    max_retries=1
                )
            
            elif "multi_step_decomposition" in classification_analysis:
                # Decompose and solve recursively
                subproblems = await self.decompose(
                    instruction="""Break this problem into minimal, independent subproblems. Each subproblem should:
                    - Be solvable in isolation
                    - Have clear input/output specifications
                    - Contribute directly to the final solution
                    - Be as granular as possible without losing meaning
                    Return list of subproblems with dependencies.""",
                    context=problem_profile
                )
                
                # In a full implementation, we would recursively solve each subproblem
                # For this workflow, we'll generate a comprehensive solution instead
                solution = await self.programmer(
                    instruction=f"""Generate a comprehensive solution that addresses all subproblems:
                    {subproblems}
                    
                    Follow all requirements from problem profile. Return ONLY the function implementation.""",
                    context=f"{problem_profile}\n\nSUBPROBLEMS:\n{subproblems}",
                    max_retries=1
                )
            
            else:
                # Default to comprehensive generation
                solution = await self.programmer(
                    instruction=f"""Generate Python code to solve this problem:
                    {problem_profile}
                    
                    Return ONLY the function implementation with necessary imports.""",
                    context=problem_profile,
                    max_retries=1
                )
            
            # Phase 4: Validation and refinement loop
            validation = await self.generate(
                instruction=f"""Critically validate this solution:
                {solution}
                
                Check for:
                - Correct function signature
                - Proper handling of edge cases identified in profile
                - Correct return types
                - Logical consistency with problem requirements
                - Potential bugs or oversights
                
                If solution is valid, respond with "VALID: <brief confirmation>".
                If solution has issues, respond with "INVALID: <specific issues and required fixes>".""",
                context=f"PROBLEM PROFILE:\n{problem_profile}\n\nSOLUTION:\n{solution}"
            )
            
            if "VALID:" in validation:
                break
            else:
                # Revise based on validation feedback
                solution = await self.revise(
                    instruction=f"""Revise the solution to fix these issues:
                    {validation}
                    
                    Maintain all original requirements. Return ONLY the corrected function implementation.""",
                    context=solution
                )
        
        # Final output sanitization
        final_output = await self.generate(
            instruction="""Extract ONLY the Python function implementation from the following text. 
            Remove any explanatory text, markdown formatting, or additional commentary.
            Return the pure Python code starting with imports (if any) and function definition.
            Ensure the code is properly formatted and indented.""",
            context=solution
        )
        
        return final_output