# Workflow ID: humaneval_33_0
# Benchmark: humaneval
# Data Indices: [77, 118]

class Workflow:
    def __init__(self, config, problem) -> None:
        self.config = config
        self.problem_text = problem
        self.llm = create(config)
        
        self.generate = operator.Generate(self.llm, self.problem_text)
        self.revise = operator.Revise(self.llm, self.problem_text)
        self.summarize = operator.Summarize(self.llm, self.problem_text)
        self.ensemble = operator.Ensemble(self.llm, self.problem_text)

    async def run_workflow(self):
        import asyncio
        import re

        # Stage 1: Problem Classification and Requirement Extraction
        problem_analysis = await self.generate(
            instruction="""Perform a deep structural analysis of this code generation problem. Extract:
            1. The core functionality required (what the function must DO)
            2. Input type and constraints (what kind of input is guaranteed)
            3. Output type and format (what must be returned, including exact type like int/float/bool/string)
            4. Behavioral patterns from examples (what transforms input to output)
            5. Edge cases implied by examples (like 0, negative numbers, empty strings, single characters)
            6. Problem type classification: mathematical, string manipulation, list processing, algorithmic, or other
            7. Any hidden constraints or assumptions (like case sensitivity, performance requirements, etc.)
            Present your analysis in a structured, bullet-point format with clear headings for each section.""",
            context=""
        )

        # Stage 2: Parallel Solution Generation with Diverse Strategies
        solution_candidates = await asyncio.gather(
            self.generate(
                instruction=f"""Generate a Python function implementation based on the following analysis:
                {problem_analysis}
                
                Strategy 1: Direct Implementation
                - Implement the most straightforward approach that matches the examples
                - Focus on correctness over optimization
                - Handle all edge cases mentioned in the analysis
                - Return exactly the type specified in the examples""",
                context=""
            ),
            self.generate(
                instruction=f"""Generate a Python function implementation based on the following analysis:
                {problem_analysis}
                
                Strategy 2: Mathematical/Algorithmic Approach
                - Look for mathematical patterns or formulas in the examples
                - Use computational logic rather than brute force
                - Consider numerical precision, integer vs float, etc.
                - Ensure edge cases are handled mathematically""",
                context=""
            ),
            self.generate(
                instruction=f"""Generate a Python function implementation based on the following analysis:
                {problem_analysis}
                
                Strategy 3: Defensive Programming Approach
                - Explicitly handle all edge cases identified in analysis
                - Use clear conditionals and explicit checks
                - Prioritize readability and maintainability
                - Include no optimizations or clever tricks - just clear, correct code""",
                context=""
            )
        )

        # Stage 3: Ensemble Selection - Synthesize Best Solution
        selected_solution = await self.ensemble(
            instruction="""Evaluate these three candidate solutions and select or synthesize the best one. Criteria:
            1. Correctness: Must satisfy all examples in the specification
            2. Edge Case Handling: Must explicitly handle all edge cases identified in analysis
            3. Return Type: Must match exactly what's shown in examples (int vs float, string vs None, etc.)
            4. Simplicity: Prefer simpler, more direct implementations over complex ones
            5. No Over-engineering: Must not include any functionality beyond what's specified
            6. Function Name: Must exactly match the ENTRY POINT specified in the problem
            
            If one solution is clearly superior, select it. If they have complementary strengths, synthesize a new solution combining the best elements of each. Return ONLY the final Python code, nothing else.""",
            contexts_list=solution_candidates
        )

        # Stage 4: Self-Critique and Validation
        critique = await self.generate(
            instruction=f"""Critically review this code against the original specification:
            {selected_solution}
            
            Checklist:
            1. Does it handle ALL examples shown in the docstring? Verify each one.
            2. Does it handle ALL edge cases identified in our analysis? List them and verify.
            3. Does it return EXACTLY the type shown in examples? (e.g., bool not 0/1, string not None)
            4. Is the function name EXACTLY as specified in ENTRY POINT?
            5. Does it avoid over-engineering? (no extra features, optimizations, or comments unless necessary)
            6. Are there any logical flaws or boundary condition errors?
            
            If any issues are found, describe them specifically. If no issues, state 'PASSES ALL CHECKS'.""",
            context=selected_solution
        )

        # Stage 5: Revision Based on Critique
        if "PASSES ALL CHECKS" not in critique:
            final_solution = await self.revise(
                instruction=f"""Revise this code to fix the issues identified in the critique:
                {critique}
                
                Requirements:
                1. Fix all identified issues while preserving correct functionality
                2. Maintain exact function name as specified in ENTRY POINT
                3. Ensure return types match examples exactly
                4. Handle all edge cases
                5. Keep code as simple and direct as possible
                6. Return ONLY the corrected Python code, nothing else""",
                context=selected_solution
            )
        else:
            final_solution = selected_solution

        # Stage 6: Final Verification and Cleanup
        verified_solution = await self.revise(
            instruction="""Final verification step:
            1. Ensure function name exactly matches ENTRY POINT (case-sensitive)
            2. Remove any unnecessary comments, imports, or whitespace
            3. Ensure code is clean, minimal, and matches specification exactly
            4. Return ONLY the final Python function code, nothing else""",
            context=final_solution
        )

        return verified_solution