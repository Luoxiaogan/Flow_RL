# Workflow ID: mbppplus_117_0
# Benchmark: mbppplus
# Data Indices: [99, 137, 250]

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

        # Step 1: Deep structural analysis of the problem
        analysis = await self.generate(
            instruction="""Perform a comprehensive analysis of this programming problem:
            1. Identify input parameters and their expected types (list, int, string, etc.)
            2. Determine the exact output type and format required
            3. Infer constraints and edge cases from the test cases (empty inputs, single elements, duplicates, boundaries)
            4. Classify the problem type: iterative, recursive, mathematical, string-based, or logical
            5. Propose at least three distinct solution strategies with their pros/cons
            6. Highlight any potential pitfalls or common mistakes
            7. Suggest optimal data structures and algorithms
            Format your response as a structured markdown document with clear sections.""",
            context=""
        )

        # Step 2: Parallel generation of multiple solution strategies
        solution_strategies = [
            """Implement an IMPERATIVE solution:
            - Use explicit loops and conditionals
            - Prioritize readability and straightforward logic
            - Include comprehensive edge-case handling
            - Add inline comments explaining key steps
            - Return exactly the required data type""",
            
            """Implement a FUNCTIONAL solution:
            - Use map/filter/reduce patterns where applicable
            - Leverage built-in functions and comprehensions
            - Focus on immutability and expression-based logic
            - Include type hints in comments if helpful
            - Ensure output matches exact specification""",
            
            """Implement a MATHEMATICAL/OPTIMIZED solution:
            - Look for closed-form formulas or mathematical shortcuts
            - Minimize computational complexity
            - Use mathematical insights from the problem analysis
            - Include derivation comments if non-obvious
            - Handle floating-point precision if relevant"""
        ]

        # Generate solutions in parallel
        solution_tasks = [
            self.generate(
                instruction=f"""Based on this analysis:
                {analysis}
                
                {strategy}
                
                IMPORTANT: 
                - Match the exact function signature from the problem
                - Handle ALL edge cases identified in analysis
                - Return correct data type (list vs tuple vs scalar)
                - Include no extra output or print statements
                - Code must be self-contained with necessary imports""",
                context=analysis
            ) for strategy in solution_strategies
        ]
        
        initial_solutions = await asyncio.gather(*solution_tasks)

        # Step 3: Parallel revision and validation of each solution
        revision_tasks = [
            self.revise(
                instruction=f"""Critically review this solution:
                - Verify correctness against all test cases
                - Check edge case handling (empty inputs, boundaries, etc.)
                - Improve code clarity and variable naming
                - Fix any logical errors or type mismatches
                - Add defensive checks for invalid inputs
                - Ensure output format exactly matches requirements
                - Optimize if obvious improvements exist
                Return ONLY the corrected Python code with no additional text.""",
                context=solution
            ) for solution in initial_solutions
        ]
        
        revised_solutions = await asyncio.gather(*revision_tasks)

        # Step 4: Ensemble synthesis - combine the best elements
        final_solution = await self.ensemble(
            instruction="""Select and synthesize the optimal solution:
            CRITERIA:
            1. Correctness: Must handle all edge cases and test scenarios
            2. Clarity: Code should be readable and well-structured
            3. Efficiency: Prefer optimal time/space complexity
            4. Robustness: Include defensive programming practices
            5. Specification compliance: Exact function signature and return type
            
            If multiple solutions are equally valid, create a HYBRID that:
            - Takes the clearest structure from one solution
            - Incorporates the most efficient algorithm from another
            - Adds the most comprehensive edge-case handling from a third
            
            Return ONLY the final Python code with no additional text or explanations.""",
            contexts_list=revised_solutions
        )

        # Step 5: Final verification and cleanup
        verified_solution = await self.revise(
            instruction="""Final verification and cleanup:
            1. Ensure code matches EXACT function signature from original problem
            2. Remove any unnecessary imports or comments
            3. Verify all edge cases are handled (empty inputs, single elements, etc.)
            4. Confirm return type is exactly as specified (int, float, list, tuple, etc.)
            5. Check for any remaining logical errors or oversights
            6. Format code to be clean and minimal
            
            Return ONLY the final Python code with no additional text.""",
            context=final_solution
        )

        return verified_solution