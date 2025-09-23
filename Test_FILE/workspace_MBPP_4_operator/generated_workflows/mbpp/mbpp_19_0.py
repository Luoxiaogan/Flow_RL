# Workflow ID: mbpp_19_0
# Benchmark: mbpp
# Data Indices: [49]

import asyncio
import re

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
        # --- ALL IMPORTS MUST GO HERE INSIDE THE METHOD ---
        import re

        # Phase 1: Problem Analysis
        # Step 1: Extract function name and parameters
        function_info = await self.generate(
            instruction="""Extract the function name and its parameters from the assert statements.
            Format as:
            Function Name: [name]
            Parameters: [param1, param2, ...]
            Return Type: [type]""",
            context=""
        )

        # Step 2: Parse natural language description
        task_analysis = await self.generate(
            instruction=f"""Based on the following function information:
            {function_info}
            
            Analyze the natural language description to identify:
            - Key operations (e.g., sorting, filtering)
            - Implicit constraints
            - Expected behavior""",
            context=function_info
        )

        # Step 3: Identify edge cases
        edge_cases = await self.generate(
            instruction=f"""Given the task analysis:
            {task_analysis}
            
            Identify potential edge cases, such as:
            - Empty inputs
            - Negative values
            - Mismatched data types""",
            context=task_analysis
        )

        # Phase 2: Solution Exploration
        # Step 4: Generate multiple candidate solutions
        candidates = await asyncio.gather(
            self.generate(
                instruction=f"""Generate a solution assuming sorting is required.
                Task Analysis: {task_analysis}
                Edge Cases: {edge_cases}""",
                context=task_analysis
            ),
            self.generate(
                instruction=f"""Generate a solution assuming no sorting is required.
                Task Analysis: {task_analysis}
                Edge Cases: {edge_cases}""",
                context=task_analysis
            )
        )

        # Step 5: Validate candidates
        validations = await asyncio.gather(
            *[self.generate(
                instruction=f"""Validate the following solution against the test cases:
                Solution: {candidate}""",
                context=candidate
            ) for candidate in candidates]
        )

        # Filter valid candidates
        valid_candidates = [c for c, v in zip(candidates, validations) if "error" not in v.lower()]

        # Phase 3: Refinement and Synthesis
        # Step 6: Refine valid candidates
        refined = await asyncio.gather(
            *[self.revise(
                instruction=f"""Improve the following solution:
                - Fix syntax errors
                - Optimize logic
                - Ensure proper indentation and imports
                Solution: {candidate}""",
                context=candidate
            ) for candidate in valid_candidates]
        )

        # Step 7: Synthesize final solution
        final_solution = await self.ensemble(
            instruction=f"""Select the most robust and generalizable solution.
            Candidates: {refined}""",
            contexts_list=refined
        )

        # Phase 4: Final Validation
        # Step 8: Confirm correctness
        final_validation = await self.generate(
            instruction=f"""Validate the final solution against all test cases:
            Solution: {final_solution}""",
            context=final_solution
        )

        # If issues persist, trigger iterative refinement
        if "error" in final_validation.lower():
            final_solution = await self.revise(
                instruction=f"""Fix remaining issues:
                Validation Feedback: {final_validation}
                Solution: {final_solution}""",
                context=final_solution
            )

        return final_solution