# Workflow ID: mbppplus_137_0
# Benchmark: mbppplus
# Data Indices: [166, 43]

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
        
        # Phase 1: Problem Analysis and Requirement Extraction
        analysis_instruction = """
        Analyze the programming problem thoroughly and extract the following:
        1. Exact function signature that must be implemented (function name and parameters)
        2. Expected input types and constraints
        3. Expected output type and format
        4. Key edge cases to handle (empty inputs, single elements, boundary conditions, etc.)
        5. Algorithmic approach suggestions (brute force, optimized, etc.)
        6. Any special requirements mentioned in the problem description
        7. Similar problems and their typical solutions
        8. Potential pitfalls and common mistakes to avoid
        
        Structure your analysis clearly with headings for each section.
        Be comprehensive and detailed - this analysis will guide code generation.
        """
        
        problem_analysis = await self.generate(
            instruction=analysis_instruction,
            context=""
        )
        
        # Phase 2: Generate Multiple Solution Approaches in Parallel
        # This creates diversity in solution strategies
        solution_approaches = await asyncio.gather(
            self.generate(
                instruction=f"""
                Based on this analysis:
                {problem_analysis}
                
                Generate a BRUTE FORCE solution approach. Focus on:
                - Simplicity and correctness
                - Handling all edge cases identified in the analysis
                - Following the exact function signature
                - Clear, readable code
                - Comprehensive comments explaining the logic
                """,
                context=problem_analysis
            ),
            self.generate(
                instruction=f"""
                Based on this analysis:
                {problem_analysis}
                
                Generate an OPTIMIZED solution approach. Focus on:
                - Algorithmic efficiency (time/space complexity)
                - Clever use of data structures or Python features
                - Handling all edge cases identified in the analysis
                - Following the exact function signature
                - Clear, readable code with efficiency comments
                """,
                context=problem_analysis
            ),
            self.generate(
                instruction=f"""
                Based on this analysis:
                {problem_analysis}
                
                Generate a PYTHONIC solution approach. Focus on:
                - Leveraging Python's built-in functions and idioms
                - Concise, elegant code
                - Handling all edge cases identified in the analysis
                - Following the exact function signature
                - Readability and maintainability
                """,
                context=problem_analysis
            )
        )
        
        # Phase 3: Convert Approaches to Code Implementations
        code_implementations = await asyncio.gather(
            *[self.programmer(
                instruction=f"""
                Convert this solution approach into a complete Python function implementation:
                {approach}
                
                CRITICAL REQUIREMENTS:
                - Use the EXACT function name and parameters from the original problem
                - Include all necessary imports at the top of the function
                - Return the EXACT data type expected (list, tuple, set, etc.)
                - Handle all edge cases mentioned in the analysis
                - Code must be syntactically correct and follow Python best practices
                - Output ONLY the function implementation, nothing else
                - Format: 
                # imports if needed
                def function_name(params):
                    # implementation
                    return result
                
                Ensure robustness and correctness above all else.
                """,
                context=approach,
                max_retries=3
            ) for approach in solution_approaches]
        )
        
        # Phase 4: Ensemble - Select the Best Implementation
        best_implementation = await self.ensemble(
            instruction="""
            Evaluate these code implementations and select the BEST one based on:
            1. Correctness: Does it handle all edge cases and requirements?
            2. Efficiency: Is it algorithmically efficient?
            3. Readability: Is the code clear and well-structured?
            4. Pythonic: Does it use Python idioms appropriately?
            5. Robustness: Does it handle unexpected inputs gracefully?
            
            If multiple implementations are equally good, prefer the most readable and maintainable.
            Return ONLY the selected implementation, nothing else.
            """,
            contexts_list=code_implementations
        )
        
        # Phase 5: Final Validation and Refinement
        final_implementation = await self.revise(
            instruction="""
            Review this final implementation and make any necessary improvements:
            - Ensure it follows the EXACT function signature from the original problem
            - Verify all edge cases are handled
            - Check return type matches requirements
            - Improve code clarity if needed
            - Add comments for complex logic
            - Ensure no syntax errors
            - Remove any unnecessary code or imports
            - Output ONLY the function implementation, nothing else
            
            This is the final version that will be submitted, so make it perfect.
            """,
            context=best_implementation
        )
        
        return final_implementation