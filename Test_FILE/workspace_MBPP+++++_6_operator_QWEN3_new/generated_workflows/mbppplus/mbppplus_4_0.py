# Workflow ID: mbppplus_4_0
# Benchmark: mbppplus
# Data Indices: [357, 276]

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

        # Step 1: Parallel problem analysis from multiple perspectives
        analysis_instructions = [
            """Analyze this programming problem from a DATA TRANSFORMATION perspective:
            - What are the input and output data types?
            - What kind of transformation is required (sorting, mapping, filtering, etc.)?
            - Are there any type conversion requirements?
            - What edge cases relate to data structure (empty, single element, duplicates)?
            Provide a structured analysis focusing on data flow and type handling.""",
            
            """Analyze this programming problem from an ALGORITHMIC perspective:
            - Does this require iteration, recursion, or mathematical computation?
            - Are there known algorithms or patterns that apply (greedy, DP, etc.)?
            - What is the computational complexity of potential solutions?
            - What edge cases relate to algorithmic behavior (boundaries, overflow, etc.)?
            Provide a structured analysis focusing on algorithmic approach and complexity.""",
            
            """Analyze this programming problem from an EDGE CASE & ROBUSTNESS perspective:
            - What are all possible edge cases (empty input, single element, extreme values)?
            - What validation or error handling might be needed?
            - Are there any constraints on input size or format?
            - What would cause a solution to fail?
            Provide a structured analysis focusing on robustness and failure modes."""
        ]

        analyses = await asyncio.gather(
            *[self.generate(instruction=instr, context="") for instr in analysis_instructions]
        )

        # Step 2: Ensemble the analyses into a unified problem understanding
        unified_analysis = await self.ensemble(
            instruction="""Synthesize these three analyses into a single, comprehensive problem understanding:
            - Combine insights about data types, algorithms, and edge cases
            - Identify the most appropriate solution strategy (code-based or direct transformation)
            - Determine if decomposition into subproblems is necessary
            - Highlight the most critical edge cases to handle
            - Recommend whether to use programmer operator or generate+revise approach
            Format as a structured decision report with clear recommendations.""",
            contexts_list=analyses
        )

        # Step 3: Conditional branching based on problem type
        strategy_decision = await self.generate(
            instruction=f"""Based on this unified analysis:
            {unified_analysis}
            
            Make a binary decision: Should this problem be solved using:
            A) The programmer operator (for algorithmic/mathematical problems requiring code)
            B) The generate+revise approach (for direct transformations, string/list operations)
            
            Respond ONLY with 'A' or 'B'.""",
            context=unified_analysis
        )

        final_solution = ""
        
        if "A" in strategy_decision.upper():
            # Code-based solution path
            # First, generate detailed code specification
            code_spec = await self.generate(
                instruction=f"""Based on the problem analysis:
                {unified_analysis}
                
                Create a detailed specification for the code solution:
                - Exact function signature (name, parameters)
                - Expected input/output types and formats
                - Key algorithmic steps or logic flow
                - Specific edge cases to handle in code
                - Any required imports or dependencies
                Format as a clear, structured specification for a programmer.""",
                context=unified_analysis
            )
            
            # Generate code with validation loop
            code_attempt = await self.programmer(
                instruction=f"""Implement the solution according to this specification:
                {code_spec}
                
                Requirements:
                - Handle all edge cases identified in analysis
                - Return correct data type as specified
                - Include necessary imports within function if needed
                - Write clean, efficient, readable code
                - Do NOT include test cases or explanations - only the function implementation""",
                context=code_spec,
                max_retries=3
            )
            
            # Validate and refine code
            for _ in range(3):
                validation = await self.generate(
                    instruction=f"""Critically review this code solution:
                    {code_attempt}
                    
                    Check for:
                    - Correct handling of all edge cases
                    - Proper return type and format
                    - Code efficiency and readability
                    - Adherence to specification
                    - Any logical errors or oversights
                    If perfect, respond 'VALID'. Otherwise, provide specific revision instructions.""",
                    context=code_attempt
                )
                
                if "VALID" in validation.upper():
                    final_solution = code_attempt
                    break
                else:
                    code_attempt = await self.revise(
                        instruction=f"""Revise the code based on this feedback:
                        {validation}
                        
                        Requirements:
                        - Fix all identified issues
                        - Maintain correct function signature
                        - Preserve all edge case handling
                        - Return only the function implementation, no explanations""",
                        context=code_attempt
                    )
            final_solution = code_attempt
            
        else:
            # Direct transformation solution path
            initial_solution = await self.generate(
                instruction=f"""Based on the problem analysis:
                {unified_analysis}
                
                Provide a direct solution to the problem:
                - Describe the exact transformation or operation needed
                - Specify handling of edge cases
                - Indicate expected output format
                - If applicable, provide Python code for the transformation
                Focus on clarity and precision.""",
                context=unified_analysis
            )
            
            # Refine into pure function implementation
            final_solution = await self.revise(
                instruction="""Extract and format ONLY the Python function implementation:
                - Remove all explanations, comments, and markdown
                - Ensure correct function signature as specified in original problem
                - Include necessary imports inside the function if needed
                - Return only the raw code, nothing else
                - Ensure it handles all edge cases identified in analysis""",
                context=initial_solution
            )

        # Final cleanup: ensure only function implementation is returned
        clean_code = await self.revise(
            instruction="""Final cleanup: Return ONLY the Python function implementation.
            - Remove any remaining explanations, comments, or markdown formatting
            - Ensure imports are inside the function if needed
            - Verify function signature matches exactly what's required
            - No test cases, no examples, no additional text
            Return ONLY the raw code.""",
            context=final_solution
        )

        return clean_code