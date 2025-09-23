# Workflow ID: mbppplus_113_0
# Benchmark: mbppplus
# Data Indices: [297, 206, 288]

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
        Universal workflow for programming problem solving domain.
        Combines analysis, conditional branching, parallel generation, 
        ensemble synthesis, and final revision for robust solutions.
        """
        import asyncio
        import re

        # Phase 1: Deep problem analysis
        problem_analysis = await self.generate(
            instruction="""Perform comprehensive problem analysis:
            1. Identify the core task: What transformation or computation is required?
            2. Extract all explicit requirements from function signature and test cases
            3. Infer implicit requirements: What edge cases are likely? (empty inputs, single elements, duplicates, boundary values)
            4. Classify problem type: Is it about searching, filtering, transforming, counting, or restructuring?
            5. Identify data types involved and required return types
            6. Note any performance or efficiency considerations
            7. What common Python patterns or libraries might be applicable?
            8. What are the most likely failure modes or tricky edge cases?
            
            Structure your analysis clearly with numbered sections for each point above.
            Think like a test designer - anticipate what additional test cases might be included beyond those shown.""",
            context=""
        )

        # Phase 2: Generate multiple solution approaches in parallel
        # Each approach has a different focus to ensure coverage
        solution_attempts = await asyncio.gather(
            self.generate(
                instruction=f"""Generate solution attempt #1 - Direct approach:
                Based on the problem analysis: {problem_analysis}
                
                Implement the most straightforward, readable solution that directly addresses the requirements.
                Focus on clarity and correctness over optimization.
                Include all necessary imports inside the function if needed.
                Handle edge cases explicitly as identified in the analysis.
                Return exactly the required data type (list, tuple, set, etc.).""",
                context=problem_analysis
            ),
            self.generate(
                instruction=f"""Generate solution attempt #2 - Edge case focused:
                Based on the problem analysis: {problem_analysis}
                
                Implement a solution that prioritizes robustness and edge case handling.
                Explicitly handle: empty inputs, single elements, duplicates, boundary conditions.
                Use defensive programming techniques.
                Consider using built-in functions or itertools where appropriate.
                Ensure type consistency and proper return types.
                Write code that would pass extensive test suites including edge cases.""",
                context=problem_analysis
            ),
            self.generate(
                instruction=f"""Generate solution attempt #3 - Optimized/elegant approach:
                Based on the problem analysis: {problem_analysis}
                
                Implement the most elegant or efficient solution possible.
                Consider using Python idioms, comprehensions, or functional approaches.
                Optimize for performance if applicable, but don't sacrifice correctness.
                Use appropriate data structures for the task.
                Ensure the solution is still readable and maintainable.
                Match the exact function signature and return type requirements.""",
                context=problem_analysis
            )
        )

        # Phase 3: Ensemble synthesis - combine the best elements
        final_solution = await self.ensemble(
            instruction="""Synthesize the best solution from all attempts:
            Evaluate all three solution attempts against these criteria:
            1. Correctness: Does it handle all base cases correctly?
            2. Edge case coverage: Does it handle empty inputs, single elements, duplicates, boundaries?
            3. Efficiency: Is the solution reasonably efficient for the problem size?
            4. Readability: Is the code clear and maintainable?
            5. Requirements compliance: Does it match function signature, return types, and formatting?
            
            Create a final solution that combines the strongest elements from each attempt.
            Prioritize correctness and edge case handling over elegance.
            Ensure the solution is production-ready and would pass extensive test suites.
            Format the output as pure Python code with the exact function signature required.
            Include imports inside the function if needed.
            Return only the function implementation, nothing else.""",
            contexts_list=solution_attempts
        )

        # Phase 4: Final revision for strict compliance
        polished_solution = await self.revise(
            instruction="""Revise for strict compliance with requirements:
            1. Verify the function name exactly matches the required signature
            2. Ensure parameter names are exactly as specified
            3. Check that all necessary imports are included at the top of the function
            4. Confirm return type matches exactly what's expected (list vs tuple vs set)
            5. Remove any extra text, comments, or explanations - return ONLY the function code
            6. Ensure the code handles all edge cases mentioned in the problem's note about extensive additional test cases
            7. Format the code cleanly with proper indentation
            
            The output must be ready for direct execution - no markdown, no explanations, just the Python function.""",
            context=final_solution
        )

        return polished_solution