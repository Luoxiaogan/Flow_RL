# Workflow ID: mbpp_59_0
# Benchmark: mbpp
# Data Indices: [328]

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
        import re
        
        # Step 1: Initial Analysis
        function_info = await self.generate(
            instruction="""Extract the function name and analyze the task:
            - Identify the function name from assert statements
            - Summarize the task description
            - List input types and expected outputs""",
            context=""
        )
        
        # Step 2: Parallel Exploration
        solutions = await asyncio.gather(
            self.generate(
                instruction=f"""Generate a direct translation solution:
                - Follow the task description closely
                - Use standard library functions where applicable
                Function info: {function_info}""",
                context=""
            ),
            self.generate(
                instruction=f"""Generate an algorithmic solution:
                - Focus on logical steps and algorithms
                - Consider edge cases and optimizations
                Function info: {function_info}""",
                context=""
            )
        )
        
        # Step 3: Synthesis and Refinement
        best_solution = await self.ensemble(
            instruction=f"""Select the best solution or synthesize a new one:
            - Evaluate correctness and completeness
            - Consider edge cases and robustness
            Solutions: {solutions}""",
            contexts_list=solutions
        )
        
        refined_solution = await self.revise(
            instruction=f"""Refine the selected solution:
            - Improve clarity and readability
            - Ensure proper use of Python idioms
            - Add necessary comments and documentation
            Solution: {best_solution}""",
            context=best_solution
        )
        
        # Step 4: Validation and Finalization
        validation = await self.generate(
            instruction=f"""Validate the refined solution:
            - Check against all assert statements
            - Ensure proper imports and indentation
            - Verify adherence to Python coding standards
            Solution: {refined_solution}""",
            context=refined_solution
        )
        
        final_code = await self.revise(
            instruction=f"""Finalize the code:
            - Incorporate any remaining feedback from validation
            - Ensure complete and executable code
            Validation: {validation}""",
            context=refined_solution
        )
        
        return final_code