# Workflow ID: mbpp_8_0
# Benchmark: mbpp
# Data Indices: [39, 25]

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

        # Step 1: Extract function name, inputs, and outputs
        analysis = await self.generate(
            instruction="""Extract the function name from the assert statements.
            Identify input types and expected outputs from the test cases.
            Summarize the task requirements in structured format.""",
            context=""
        )

        # Step 2: Generate multiple solution strategies in parallel
        strategies = await asyncio.gather(
            self.generate(
                instruction=f"Using the extracted information: {analysis}\n"
                            "Develop a solution using built-in Python functions.",
                context=analysis
            ),
            self.generate(
                instruction=f"Using the extracted information: {analysis}\n"
                            "Develop a solution using standard library modules like re, math, etc.",
                context=analysis
            ),
            self.generate(
                instruction=f"Using the extracted information: {analysis}\n"
                            "Develop a solution using custom algorithms or logic.",
                context=analysis
            )
        )

        # Step 3: Synthesize the best solution
        best_solution = await self.ensemble(
            instruction="Evaluate and select the most efficient and accurate solution.",
            contexts_list=strategies
        )

        # Step 4: Refine and validate the solution iteratively
        max_iterations = 3
        for i in range(max_iterations):
            validation = await self.generate(
                instruction=f"Validate the solution against test cases. Highlight any errors or ambiguities.\nSolution:\n{best_solution}",
                context=best_solution
            )
            if "error" not in validation.lower():
                break
            best_solution = await self.revise(
                instruction=f"Fix the following issues: {validation}\nImprove clarity and correctness.",
                context=best_solution
            )

        # Step 5: Finalize the solution
        finalized_code = await self.revise(
            instruction="Ensure proper syntax, indentation, and completeness of imports. Format the code for readability.",
            context=best_solution
        )

        return finalized_code