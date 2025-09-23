# Workflow ID: mbppplus_68_0
# Benchmark: mbppplus
# Data Indices: [130, 301, 51]

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
        """
        Universal workflow for programming problem domain.
        Adapts strategy based on problem type, generates multiple solutions,
        refines for edge cases and format compliance.
        """
        import asyncio
        import re
        
        # Step 1: Classify problem type and extract requirements
        classification = await self.generate(
            instruction="""Analyze this programming problem in depth:
            1. Categorize the problem type (mathematical, data structure, string manipulation, etc.)
            2. Identify required operations (calculations, transformations, aggregations, etc.)
            3. List potential edge cases (empty inputs, single elements, boundary conditions, type mismatches)
            4. Determine expected output format and data types
            5. Note any constraints or special requirements mentioned or implied
            6. Suggest 2-3 different solution approaches that could work
            Be thorough and specific. This analysis will guide the solution strategy.""",
            context=""
        )
        
        # Step 2: Generate multiple solution attempts in parallel
        solution_attempts = await asyncio.gather(
            self.generate(
                instruction=f"""Based on this classification:
                {classification}
                
                Generate a solution attempt using approach 1 (direct implementation):
                - Write clean, readable code
                - Include necessary imports
                - Handle edge cases mentioned in classification
                - Match exact function signature from problem
                - Return appropriate data types
                - Focus on correctness over optimization initially""",
                context=classification
            ),
            self.generate(
                instruction=f"""Based on this classification:
                {classification}
                
                Generate a solution attempt using approach 2 (alternative method):
                - Use a different algorithmic approach than attempt 1
                - Consider built-in functions or libraries that might help
                - Include comprehensive edge case handling
                - Ensure output format matches requirements exactly
                - Write defensive code that handles unexpected inputs""",
                context=classification
            ),
            self.generate(
                instruction=f"""Based on this classification:
                {classification}
                
                Generate a solution attempt using approach 3 (robust/error-tolerant):
                - Prioritize handling all edge cases
                - Include input validation if appropriate
                - Use clear variable names and comments if needed
                - Ensure type consistency throughout
                - Format output exactly as specified in problem""",
                context=classification
            )
        )
        
        # Step 3: Ensemble - select or synthesize best solution
        ensembled_solution = await self.ensemble(
            instruction="""Evaluate these solution attempts and create the optimal solution:
            1. Compare correctness - which solution best addresses the problem requirements?
            2. Check edge case handling - which solution is most robust?
            3. Verify output format - which solution matches the required format exactly?
            4. Assess code quality - which is most readable and maintainable?
            5. Synthesize the best elements from multiple solutions if needed
            6. Ensure the final solution includes all necessary imports
            7. Confirm the function signature matches exactly
            Return ONLY the final function implementation with imports, nothing else.""",
            contexts_list=solution_attempts
        )
        
        # Step 4: Revise for format compliance and edge cases
        final_solution = await self.revise(
            instruction="""Refine this solution to ensure perfection:
            1. Verify function name and parameters match exactly
            2. Check that imports are included and correct
            3. Ensure return type matches requirements (list vs tuple vs set)
            4. Handle all edge cases: empty inputs, single elements, duplicates, boundary conditions
            5. Remove any unnecessary code or comments
            6. Ensure output format is exactly as specified
            7. Confirm no type mismatches or conversion errors
            8. Return ONLY the function implementation with necessary imports at top
            
            Common pitfalls to avoid:
            - Forgetting to handle empty inputs
            - Mixing up data types in return value
            - Not considering duplicate elements
            - Missing edge cases like negative numbers
            - Assuming input is always valid without checking
            
            The solution must be robust enough to pass extensive test cases beyond those shown.""",
            context=ensembled_solution
        )
        
        # Step 5: Final validation and cleanup
        # Extract just the code block if it's wrapped in markdown
        code_pattern = r'