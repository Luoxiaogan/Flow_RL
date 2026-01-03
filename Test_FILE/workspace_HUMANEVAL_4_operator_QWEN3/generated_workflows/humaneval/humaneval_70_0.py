# Workflow ID: humaneval_70_0
# Benchmark: humaneval
# Data Indices: [107, 41]

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

    async def run_workflow(self):
        import asyncio
        import re

        # Step 1: Deep problem analysis and classification
        analysis = await self.generate(
            instruction="""Perform comprehensive problem analysis:
            1. Extract the exact function signature and ENTRY POINT name
            2. Identify problem type: mathematical pattern, algorithmic implementation, string manipulation, etc.
            3. Extract all examples from docstring with input-output pairs
            4. Note any explicit constraints or edge cases mentioned
            5. Determine if solution likely requires: formula derivation, iteration, recursion, or direct computation
            6. Assess whether examples suggest a clear mathematical pattern
            7. Identify key operations needed (palindrome check, counting, filtering, etc.)
            8. Note return type requirements from examples (int, float, tuple, etc.)
            
            Format your analysis as structured sections with clear headings.""",
            context=""
        )

        # Step 2: Parallel solution generation using different strategies
        solution_candidates = await asyncio.gather(
            # Strategy 1: Mathematical pattern recognition
            self.generate(
                instruction=f"""Generate solution by analyzing mathematical patterns:
                Based on analysis: {analysis}
                
                1. Examine input-output pairs from examples for mathematical relationships
                2. Test for common patterns: linear, quadratic, exponential, factorial, etc.
                3. If clear pattern exists, implement direct formula
                4. If no clear pattern, default to literal implementation of described procedure
                5. Ensure function name matches ENTRY POINT exactly
                6. Return type must match examples precisely
                7. Handle edge cases mentioned in analysis
                8. Code must be minimal - no over-engineering
                
                Return ONLY the Python function code, nothing else.""",
                context=analysis
            ),
            
            # Strategy 2: Literal procedural implementation
            self.generate(
                instruction=f"""Generate solution by literal implementation:
                Based on analysis: {analysis}
                
                1. Implement exactly what is described in the specification
                2. Use loops, conditionals, and basic operations as needed
                3. Follow the examples step by step
                4. Include helper functions if needed (like is_palindrome)
                5. Ensure function name matches ENTRY POINT exactly
                6. Return type must match examples precisely
                7. Handle all edge cases mentioned
                8. Code must be clean and minimal
                
                Return ONLY the Python function code, nothing else.""",
                context=analysis
            ),
            
            # Strategy 3: Optimized approach considering constraints
            self.generate(
                instruction=f"""Generate optimized solution considering constraints:
                Based on analysis: {analysis}
                
                1. Consider problem constraints (like n <= 10^3)
                2. Optimize for efficiency within constraints
                3. Use mathematical insights if they simplify implementation
                4. Avoid unnecessary computations
                5. Ensure function name matches ENTRY POINT exactly
                6. Return type must match examples precisely
                7. Handle edge cases efficiently
                8. Code must be minimal and elegant
                
                Return ONLY the Python function code, nothing else.""",
                context=analysis
            )
        )

        # Step 3: Ensemble - select or synthesize best solution
        final_solution = await self.ensemble(
            instruction=f"""Select the best solution from candidates:
            Analysis: {analysis}
            
            Evaluation criteria:
            1. Correctness: Must match all examples from specification
            2. Precision: Function name and return type must be exact
            3. Minimalism: No over-engineering, simplest solution that works
            4. Edge case handling: Must handle all mentioned edge cases
            5. Efficiency: Appropriate for given constraints
            6. Readability: Clean, understandable code
            
            If one solution clearly best, select it.
            If multiple good solutions, synthesize best elements.
            If all have flaws, create improved version.
            
            Return ONLY the final Python function code, nothing else.""",
            contexts_list=solution_candidates
        )

        # Step 4: Critical revision for specification compliance
        refined_solution = await self.revise(
            instruction="""Critically revise for exact specification compliance:
            1. Verify function name matches ENTRY POINT exactly
            2. Check return types match examples precisely (int vs float, tuple structure, etc.)
            3. Ensure all edge cases from examples are handled
            4. Remove any over-engineered components or extra functionality
            5. Simplify code to minimal necessary implementation
            6. Verify no imports are needed (or add minimal imports if absolutely necessary)
            7. Ensure code is clean and follows Python best practices
            8. Double-check against original problem specification
            
            Return ONLY the final revised Python function code, nothing else.""",
            context=final_solution
        )

        return refined_solution