# Workflow ID: mbppplus_109_0
# Benchmark: mbppplus
# Data Indices: [372, 367]

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

        # Step 1: Multi-perspective problem analysis in parallel
        analysis_tasks = [
            self.generate(
                instruction="""Analyze this programming problem from a MATHEMATICAL perspective:
                - Identify any underlying mathematical relationships or formulas
                - Look for patterns that can be expressed algebraically
                - Consider number theory, modular arithmetic, or optimization principles
                - Suggest a mathematical approach to solve it
                Provide detailed reasoning with examples if possible.""",
                context=""
            ),
            self.generate(
                instruction="""Analyze this programming problem from an ALGORITHMIC perspective:
                - Identify the core algorithmic operation needed (search, sort, transform, etc.)
                - Consider time/space complexity implications
                - Suggest step-by-step procedural approach
                - Identify potential edge cases algorithmically
                Provide pseudocode or detailed steps.""",
                context=""
            ),
            self.generate(
                instruction="""Analyze this programming problem from a DATA STRUCTURE perspective:
                - What data structures are involved or could be leveraged?
                - How should data be transformed or manipulated?
                - Consider indexing, slicing, set operations, or other structural operations
                - Identify boundary conditions related to data structure limits
                Provide specific operations and their order.""",
                context=""
            ),
            self.generate(
                instruction="""Analyze this programming problem from an EDGE CASE perspective:
                - What are the extreme or degenerate cases? (empty inputs, single elements, max values)
                - What input variations could break a naive solution?
                - What are the implicit constraints or assumptions?
                - How should the solution handle invalid or unexpected inputs?
                List specific test cases that must be handled.""",
                context=""
            )
        ]
        
        analyses = await asyncio.gather(*analysis_tasks)
        
        # Step 2: Synthesize analyses into unified solution strategy
        solution_strategy = await self.ensemble(
            instruction="""Synthesize the four analytical perspectives into a unified solution strategy:
            - Combine mathematical insights with algorithmic steps
            - Integrate data structure operations with edge case handling
            - Resolve any contradictions between perspectives
            - Prioritize the most efficient and robust approach
            - Specify exact function signature, parameters, and return type
            - Include handling for all identified edge cases
            Output should be a comprehensive implementation plan ready for coding.""",
            contexts_list=analyses
        )
        
        # Step 3: Generate initial code implementation
        initial_code = await self.programmer(
            instruction=f"""Generate a Python function implementation based on this strategy:
            {solution_strategy}
            
            Requirements:
            - Use EXACT function name and parameters as specified in the problem
            - Handle all edge cases identified in the analysis
            - Return correct data type (list, tuple, set, string, etc.)
            - Include necessary imports
            - Code must be efficient and readable
            - Do NOT include test cases or print statements
            - Return ONLY the function implementation as specified in output requirements""",
            context=solution_strategy
        )
        
        # Step 4: Validate and revise code through self-critique
        validation = await self.generate(
            instruction=f"""Critically evaluate this code implementation:
            {initial_code}
            
            Check for:
            - Correctness against problem requirements
            - Handling of all edge cases identified earlier
            - Proper data type handling
            - Potential off-by-one errors or index issues
            - Efficiency concerns
            - Readability and maintainability
            - Compliance with output format requirements
            
            If any issues are found, describe them specifically. If no issues, state "VALID". """,
            context=initial_code
        )
        
        # Step 5: Revise if necessary
        final_code = initial_code
        if "VALID" not in validation.upper():
            final_code = await self.revise(
                instruction=f"""Revise the code to fix these issues:
                {validation}
                
                Requirements:
                - Maintain original function signature
                - Fix all identified issues
                - Preserve handling of edge cases
                - Return ONLY the function implementation
                - Do NOT add explanatory comments or docstrings beyond what's necessary for functionality""",
                context=initial_code
            )
        
        # Step 6: Final verification and cleanup
        verified_code = await self.generate(
            instruction=f"""Perform final verification of this code:
            {final_code}
            
            Ensure:
            - Function name matches exactly what was specified
            - Parameter names are correct
            - Return type is appropriate
            - No extra output or debugging code
            - Code is minimal and focused
            - All imports are included at top of function
            - Format matches required output structure exactly
            
            Return the final, cleaned code ready for submission.""",
            context=final_code
        )
        
        return verified_code