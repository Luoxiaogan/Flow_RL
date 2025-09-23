# Workflow ID: mbpp_37_0
# Benchmark: mbpp
# Data Indices: [103]

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

        # Step 1: Analyze the problem to classify it and extract key information
        analysis = await self.generate(
            instruction="""Analyze the problem:
            1. Classify the problem type (e.g., list operations, math, strings).
            2. Extract the function name from the test cases.
            3. Identify key requirements from the natural language description.
            Provide a structured summary.""",
            context=""
        )

        # Step 2: Parallel exploration of solution strategies
        strategies = await asyncio.gather(
            self.generate(
                instruction=f"""Generate a solution using an iterative approach:
                Problem Type: {re.search(r'list|math|string', analysis, re.IGNORECASE).group()}
                Function Name: {re.search(r'assert (\w+)\(', self.problem_text).group(1)}
                Requirements: {analysis}""",
                context=""
            ),
            self.generate(
                instruction=f"""Generate a solution using a recursive approach:
                Problem Type: {re.search(r'list|math|string', analysis, re.IGNORECASE).group()}
                Function Name: {re.search(r'assert (\w+)\(', self.problem_text).group(1)}
                Requirements: {analysis}""",
                context=""
            ),
            self.generate(
                instruction=f"""Generate a solution using standard library functions:
                Problem Type: {re.search(r'list|math|string', analysis, re.IGNORECASE).group()}
                Function Name: {re.search(r'assert (\w+)\(', self.problem_text).group(1)}
                Requirements: {analysis}""",
                context=""
            )
        )

        # Step 3: Ensemble selection of the best solution
        best_solution = await self.ensemble(
            instruction="""Select the best solution based on:
            1. Correctness: Does it satisfy the test cases?
            2. Simplicity: Is the code easy to understand?
            3. Efficiency: Does it perform well?""",
            contexts_list=strategies
        )

        # Step 4: Iterative refinement
        refined_solution = best_solution
        for _ in range(3):  # Limit iterations to avoid infinite loops
            validation = await self.generate(
                instruction=f"""Validate the solution against the test cases:
                Solution: {refined_solution}
                Test Cases: {self.problem_text}""",
                context=""
            )
            if "error" in validation.lower():
                refined_solution = await self.revise(
                    instruction=f"""Fix the following issues:
                    Issues: {validation}
                    Solution: {refined_solution}""",
                    context=refined_solution
                )
            else:
                break

        # Step 5: Final validation
        final_validation = await self.generate(
            instruction=f"""Final validation:
            Solution: {refined_solution}
            Test Cases: {self.problem_text}""",
            context=""
        )

        return refined_solution