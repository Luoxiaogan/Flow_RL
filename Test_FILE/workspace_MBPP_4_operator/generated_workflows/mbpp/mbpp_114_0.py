# Workflow ID: mbpp_114_0
# Benchmark: mbpp
# Data Indices: [188, 144]

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

        # Step 1: Initial Analysis - Extract Function Name and Parameters
        analysis = await self.generate(
            instruction="""Extract the function name and parameters from the test cases.
            - Identify the function name used in the assert statements.
            - List all input parameters and their types.
            - Summarize the expected output format.
            Provide the information in a structured format.""",
            context=""
        )

        # Step 2: Parse Natural Language Description
        task_description = await self.generate(
            instruction=f"""Based on the following analysis:
            {analysis}
            
            Interpret the natural language task description:
            - Identify the inputs and outputs.
            - Describe the transformation logic in detail.
            - Highlight any assumptions or ambiguities.
            Provide a clear understanding of the task.""",
            context=analysis
        )

        # Step 3: Generate Candidate Solutions in Parallel
        candidates = await asyncio.gather(
            self.generate(
                instruction=f"""Write Python code to solve the task:
                {task_description}
                
                Focus on a mathematical approach using formulas.""",
                context=task_description
            ),
            self.generate(
                instruction=f"""Write Python code to solve the task:
                {task_description}
                
                Focus on list comprehensions or array operations.""",
                context=task_description
            ),
            self.generate(
                instruction=f"""Write Python code to solve the task:
                {task_description}
                
                Focus on using Python's standard library functions.""",
                context=task_description
            )
        )

        # Step 4: Validate and Refine Solutions
        validated_candidates = []
        for candidate in candidates:
            refined = await self.revise(
                instruction=f"""Validate the following code against the test cases:
                {candidate}
                
                Ensure it passes all assertions and handles edge cases.
                Suggest improvements if necessary.""",
                context=candidate
            )
            validated_candidates.append(refined)

        # Step 5: Select Best Solution
        final_solution = await self.ensemble(
            instruction=f"""Select the best solution from the following candidates:
            {validated_candidates}
            
            Criteria:
            - Correctness: Must pass all test cases.
            - Clarity: Code should be easy to understand.
            - Efficiency: Prefer simpler and more efficient implementations.""",
            contexts_list=validated_candidates
        )

        # Step 6: Iterative Improvement (if necessary)
        max_attempts = 3
        for attempt in range(max_attempts):
            validation = await self.generate(
                instruction=f"""Validate the final solution:
                {final_solution}
                
                Check if it passes all test cases and handles edge cases.
                If not, identify errors and suggest corrections.""",
                context=final_solution
            )
            if "error" not in validation.lower():
                break
            final_solution = await self.revise(
                instruction=f"""Fix the following issues:
                {validation}
                
                Improve the code to pass all test cases.""",
                context=final_solution
            )

        return final_solution