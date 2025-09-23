# Workflow ID: mbppplus_73_0
# Benchmark: mbppplus
# Data Indices: [243, 272, 44]

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

        # PHASE 1: Deep Problem Deconstruction
        problem_profile = await self.generate(
            instruction="""Perform a comprehensive analysis of this programming problem. Extract and structure the following:
            1. Function signature: exact name and parameters
            2. Input types and constraints: what data types are expected? Any size or value limits?
            3. Output type and format: what should be returned? Tuple, list, int, etc.
            4. Algorithmic category: is this recursive, iterative, mathematical, transformational, or logical?
            5. Edge cases: list all possible edge cases (empty inputs, zeros, negatives, single elements, duplicates, type boundaries)
            6. Performance considerations: any efficiency requirements or constraints?
            7. Hidden assumptions: what might be implied but not stated?
            Format as a structured JSON-like outline with clear section headers.""",
            context=""
        )

        # PHASE 2: Parallel Strategy Generation
        strategy_tasks = [
            self.generate(
                instruction=f"""Generate a complete Python solution based on this problem profile:
                {problem_profile}
                
                Approach 1: Iterative Solution
                - Use loops and accumulators
                - Handle edge cases explicitly
                - Focus on readability and step-by-step logic
                - Include necessary imports
                - Return EXACTLY the required type as per signature""",
                context=""
            ),
            self.generate(
                instruction=f"""Generate a complete Python solution based on this problem profile:
                {problem_profile}
                
                Approach 2: Recursive/Functional Solution
                - Use recursion or functional transformations
                - Consider base cases and termination conditions
                - Handle edge cases in base conditions
                - Include necessary imports
                - Return EXACTLY the required type as per signature""",
                context=""
            ),
            self.generate(
                instruction=f"""Generate a complete Python solution based on this problem_profile:
                {problem_profile}
                
                Approach 3: Mathematical/Direct Formula
                - Derive or apply mathematical formulas
                - Avoid unnecessary loops or recursion
                - Handle edge cases with conditional guards
                - Include necessary imports
                - Return EXACTLY the required type as per signature""",
                context=""
            )
        ]
        
        strategy_solutions = await asyncio.gather(*strategy_tasks)

        # PHASE 3: Ensemble Synthesis
        synthesized_solution = await self.ensemble(
            instruction=f"""You are given multiple solution approaches for the same programming problem. 
            Problem Profile: {problem_profile}
            
            Your task:
            1. Compare all solutions for correctness, efficiency, and adherence to signature
            2. Identify the strongest elements from each (e.g., edge case handling from one, efficiency from another)
            3. Synthesize a final solution that combines the best aspects OR select the single best solution
            4. Ensure the solution:
               - Uses exact function name and parameters
               - Returns correct data type
               - Handles all edge cases mentioned in profile
               - Is efficient and readable
               - Contains only necessary imports
            5. Output ONLY the final function implementation - no explanations, no comments unless critical""",
            contexts_list=strategy_solutions
        )

        # PHASE 4: Iterative Refinement with Validation
        current_solution = synthesized_solution
        for iteration in range(3):  # Max 3 refinement cycles
            validation_feedback = await self.generate(
                instruction=f"""Critically validate this solution against the problem requirements:
                Problem Profile: {problem_profile}
                Current Solution: {current_solution}
                
                Check for:
                1. Signature compliance: exact function name and parameters
                2. Type correctness: input handling and return type
                3. Edge case coverage: all edge cases from profile handled?
                4. Efficiency: any obvious performance bottlenecks?
                5. Code quality: clean, readable, no redundant operations
                6. Potential bugs: off-by-one, type conversion, recursion limits
                
                If any issues found, describe them specifically. If perfect, say 'VALIDATED'.""",
                context=current_solution
            )
            
            if "VALIDATED" in validation_feedback.upper():
                break
                
            current_solution = await self.revise(
                instruction=f"""Revise the solution based on this feedback:
                {validation_feedback}
                
                Problem Profile: {problem_profile}
                
                Requirements:
                - Fix all identified issues
                - Maintain exact function signature
                - Preserve correct return type
                - Keep code clean and efficient
                - Output ONLY the function implementation with necessary imports""",
                context=current_solution
            )

        # FINAL OUTPUT
        return current_solution