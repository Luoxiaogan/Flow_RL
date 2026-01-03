# Workflow ID: mbppplus_20_0
# Benchmark: mbppplus
# Data Indices: [156, 146, 292]

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

        # Step 1: Problem Analysis and Classification
        analysis = await self.generate(
            instruction="""Thoroughly analyze the programming problem. Identify:
            1. Problem category (e.g., string manipulation, dynamic programming, list operations)
            2. Input and output data types and structures
            3. Key operations required (e.g., reversal, comparison, extraction)
            4. Potential edge cases (empty inputs, single elements, duplicates)
            5. Expected return type and format
            6. Any constraints or special conditions mentioned
            Present this as a structured analysis with clear sections.""",
            context=""
        )

        # Step 2: Generate Multiple Solution Candidates in Parallel
        candidate_tasks = [
            self.generate(
                instruction=f"""Based on this analysis:
                {analysis}
                
                Generate a Python function that solves the problem. Focus on:
                - Correctness for the main case
                - Simple, readable implementation
                - Matching the exact function signature provided
                Include all necessary imports within the function if needed.""",
                context=analysis
            ),
            self.generate(
                instruction=f"""Based on this analysis:
                {analysis}
                
                Generate a Python function that solves the problem with emphasis on:
                - Handling all edge cases (empty inputs, boundary conditions)
                - Defensive programming and type safety
                - Robust error prevention
                Include all necessary imports within the function if needed.""",
                context=analysis
            ),
            self.generate(
                instruction=f"""Based on this analysis:
                {analysis}
                
                Generate a Python function that solves the problem with focus on:
                - Algorithmic efficiency and optimal approach
                - Using appropriate data structures
                - Clean, Pythonic code style
                Include all necessary imports within the function if needed.""",
                context=analysis
            )
        ]
        
        candidate_solutions = await asyncio.gather(*candidate_tasks)

        # Step 3: Ensemble - Select or Synthesize Best Solution
        selected_solution = await self.ensemble(
            instruction="""Evaluate the candidate solutions and select the best one based on:
            1. Correctness (must handle all edge cases identified in analysis)
            2. Adherence to function signature and return type
            3. Code clarity and maintainability
            4. Efficiency (but correctness is prioritized over optimization)
            If one solution is clearly superior, select it. If they have complementary strengths, synthesize a hybrid solution.
            Return ONLY the final Python function code, nothing else.""",
            contexts_list=candidate_solutions
        )

        # Step 4: Iterative Refinement Loop (up to 3 iterations)
        current_solution = selected_solution
        for iteration in range(3):
            critique = await self.revise(
                instruction=f"""Critically review this solution:
                {current_solution}
                
                Check for:
                - Correct handling of edge cases (empty inputs, single elements, etc.)
                - Exact match of expected return type (e.g., string vs int)
                - Potential off-by-one errors or logical flaws
                - Type consistency and proper imports
                - Adherence to function signature
                If no issues found, respond with 'APPROVED'. Otherwise, provide specific fixes needed.""",
                context=current_solution
            )
            
            if "APPROVED" in critique.upper():
                break
            else:
                # Generate revised solution based on critique
                current_solution = await self.generate(
                    instruction=f"""Revise this solution based on the critique:
                    {critique}
                    
                    Original solution:
                    {current_solution}
                    
                    Fix all identified issues while preserving correct functionality.
                    Return ONLY the complete Python function code, nothing else.""",
                    context=f"{current_solution}\n\nCRITIQUE: {critique}"
                )

        # Step 5: Final Validation and Formatting
        final_solution = await self.revise(
            instruction="""Ensure this code:
            1. Is a complete, standalone Python function
            2. Matches the exact function signature from the problem
            3. Includes all necessary imports at the top of the function
            4. Returns the correct data type as specified
            5. Has no extra text, explanations, or markdown formatting
            Return ONLY the clean Python code, nothing else.""",
            context=current_solution
        )

        return final_solution