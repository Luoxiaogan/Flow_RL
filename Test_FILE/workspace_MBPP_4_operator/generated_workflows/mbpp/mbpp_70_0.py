# Workflow ID: mbpp_70_0
# Benchmark: mbpp
# Data Indices: [260, 26]

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

        # Step 1: Problem Decomposition
        decomposition = await self.generate(
            instruction="""Extract the following information from the problem:
            - Function name (from test cases)
            - Input types and descriptions
            - Output type and description
            - Constraints and edge cases inferred from test cases
            Format the result as a JSON-like structure.""",
            context=""
        )

        # Step 2: Parallel Hypothesis Generation
        hypotheses = await asyncio.gather(
            self.generate(
                instruction=f"""Translate the task description directly into Python code.
                Function name: {re.search(r'assert (\w+)', decomposition).group(1)}
                Inputs and outputs: {decomposition}
                Ensure the code is complete and executable.""",
                context=decomposition
            ),
            self.generate(
                instruction=f"""Generate a solution using Python's standard library.
                Function name: {re.search(r'assert (\w+)', decomposition).group(1)}
                Inputs and outputs: {decomposition}
                Leverage appropriate modules like collections, math, etc.""",
                context=decomposition
            ),
            self.generate(
                instruction=f"""Generate a solution that explicitly handles edge cases.
                Function name: {re.search(r'assert (\w+)', decomposition).group(1)}
                Inputs and outputs: {decomposition}
                Include checks for invalid inputs and boundary conditions.""",
                context=decomposition
            )
        )

        # Step 3: Validation and Ensemble Selection
        validated_solutions = await asyncio.gather(
            *[self.revise(
                instruction="Validate this solution against the test cases. Identify and fix errors.",
                context=hypothesis
            ) for hypothesis in hypotheses]
        )

        best_solution = await self.ensemble(
            instruction="Select the best solution based on correctness, simplicity, and adherence to constraints.",
            contexts_list=validated_solutions
        )

        # Step 4: Iterative Refinement
        max_iterations = 3
        for _ in range(max_iterations):
            validation = await self.generate(
                instruction="Check if the solution passes all test cases. Identify any remaining issues.",
                context=best_solution
            )
            if "error" not in validation.lower():
                break
            best_solution = await self.revise(
                instruction=f"Refine the solution to address the following issues: {validation}",
                context=best_solution
            )

        return best_solution