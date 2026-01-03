# Workflow ID: mbppplus_79_0
# Benchmark: mbppplus
# Data Indices: [55, 209]

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
        """
        Universal workflow for algorithmic programming problems.
        Uses parallel validation and targeted revision to ensure robustness.
        """
        import asyncio
        import re

        # Phase 1: Generate initial solution with comprehensive instructions
        initial_solution = await self.generate(
            instruction="""Generate a Python function that solves the problem exactly as specified.
            
            CRITICAL REQUIREMENTS:
            1. Match the exact function signature shown in the problem
            2. Handle ALL edge cases: empty inputs, single elements, duplicates, boundary values
            3. Return the correct data type (list vs tuple vs set) as demonstrated in test cases
            4. Use efficient algorithms appropriate for the problem scale
            5. Include all necessary imports at the top of the function
            6. Do not add extra functionality, comments, or print statements unless explicitly required
            7. Ensure the solution works for the example test cases provided
            8. Write clean, readable code with appropriate variable names
            
            Common pitfalls to avoid:
            - Forgetting to handle empty inputs
            - Mixing up data types in return values
            - Off-by-one errors in loops
            - Assuming inputs are always valid
            - Not preserving order when required
            - Inefficient algorithms for large inputs
            
            Study the problem description and example test cases carefully to understand the exact requirements.
            Your solution will be tested against hundreds of hidden test cases including edge conditions.""",
            context=""
        )

        # Phase 2: Parallel validation - two independent critique paths
        critique_tasks = [
            self.generate(
                instruction="""Critically review this code for ALGORITHMIC CORRECTNESS and EDGE CASE HANDLING:
                
                1. Does the solution correctly implement the required algorithm?
                2. Are there any off-by-one errors or boundary condition issues?
                3. Does it handle empty inputs, single elements, and other edge cases?
                4. Is the logic efficient and appropriate for the problem?
                5. Does it match the behavior shown in the example test cases?
                6. Are there any logical flaws or incorrect assumptions?
                
                If you find any issues, provide specific fixes. If the code is correct, state "NO ISSUES FOUND".
                Focus on correctness and robustness above all else.""",
                context=initial_solution
            ),
            self.generate(
                instruction="""Critically review this code for TYPE SAFETY and API COMPLIANCE:
                
                1. Does the function signature exactly match what's required?
                2. Are return types correct (list vs tuple vs set vs primitive)?
                3. Are parameter types handled correctly?
                4. Are all necessary imports included?
                5. Is the code free of syntax errors and Python anti-patterns?
                6. Does it follow Python best practices for readability and maintainability?
                
                If you find any issues, provide specific fixes. If the code is correct, state "NO ISSUES FOUND".
                Focus on API compliance and type safety.""",
                context=initial_solution
            )
        ]
        
        critiques = await asyncio.gather(*critique_tasks)

        # Phase 3: Ensemble the critiques
        ensemble_critique = await self.ensemble(
            instruction="""Synthesize these two critiques into a coherent set of required fixes:
            
            1. Combine all identified issues from both critiques
            2. Prioritize critical errors that would cause test failures
            3. Remove any duplicate or redundant feedback
            4. Organize fixes by category: algorithmic, type safety, edge cases, etc.
            5. If both critiques say "NO ISSUES FOUND", return that phrase
            6. Be specific about what needs to be changed and how
            
            The goal is to produce a clear, actionable revision plan that addresses all identified issues.""",
            contexts_list=critiques
        )

        # Phase 4: Revise solution based on ensemble feedback
        final_solution = await self.revise(
            instruction="""Revise the code based on the critique feedback:
            
            1. Implement all fixes specified in the critique
            2. Maintain the original function signature and core logic unless changes are required
            3. Ensure all edge cases are properly handled
            4. Verify type safety and API compliance
            5. Keep the code clean, readable, and efficient
            6. If no issues were found, return the original code unchanged
            
            The revised code must be production-ready and pass all test cases including hidden edge cases.""",
            context=f"Original code:\n{initial_solution}\n\nCritique:\n{ensemble_critique}"
        )

        return final_solution