# Workflow ID: mbpp_54_0
# Benchmark: mbpp
# Data Indices: [2]

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
        
        # --- Initial Analysis: Extract Key Information ---
        initial_analysis = await self.generate(
            instruction="""Analyze the problem description:
            1. Extract the function name from assert statements
            2. Identify input types and expected output formats
            3. List any explicit constraints or requirements
            Provide structured information.""",
            context=""
        )
        
        # --- Parallel Exploration: Generate Multiple Solutions ---
        strategy_1 = "Use Python standard library functions where applicable."
        strategy_2 = "Implement custom algorithms without relying on external libraries."
        strategy_3 = "Optimize for performance by minimizing computational complexity."
        
        solutions = await asyncio.gather(
            self.generate(
                instruction=f"""Generate a solution using the following strategy:
                {strategy_1}
                Ensure the function name matches the test cases and include all necessary imports.""",
                context=initial_analysis
            ),
            self.generate(
                instruction=f"""Generate a solution using the following strategy:
                {strategy_2}
                Ensure the function name matches the test cases and include all necessary imports.""",
                context=initial_analysis
            ),
            self.generate(
                instruction=f"""Generate a solution using the following strategy:
                {strategy_3}
                Ensure the function name matches the test cases and include all necessary imports.""",
                context=initial_analysis
            )
        )
        
        # --- Synthesis and Selection: Choose Best Solution ---
        selected_solution = await self.ensemble(
            instruction="""Evaluate all solutions:
            1. Check compliance with test cases
            2. Assess code clarity and maintainability
            3. Prioritize solutions with fewer dependencies
            Select the most promising candidate.""",
            contexts_list=solutions
        )
        
        # --- Iterative Refinement: Validate and Improve ---
        max_iterations = 5
        for iteration in range(max_iterations):
            validation_result = await self.generate(
                instruction=f"""Validate the current solution against all test cases:
                Current Solution:
                {selected_solution}
                
                Report any errors or mismatches.""",
                context=initial_analysis
            )
            
            if "error" not in validation_result.lower() and "fail" not in validation_result.lower():
                break  # All test cases passed
            
            selected_solution = await self.revise(
                instruction=f"""Revise the solution to fix reported issues:
                Issues:
                {validation_result}
                
                Ensure the function name matches the test cases and include all necessary imports.""",
                context=selected_solution
            )
        
        # --- Final Compilation: Clean and Executable Format ---
        final_code = await self.summarize(
            instruction="""Condense the solution into a clean, executable format:
            1. Proper indentation (4 spaces)
            2. Complete imports at the top
            3. Clear comments explaining complex logic""",
            context=selected_solution
        )
        
        return final_code