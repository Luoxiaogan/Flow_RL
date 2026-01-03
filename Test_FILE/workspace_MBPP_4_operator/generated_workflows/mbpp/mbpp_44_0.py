# Workflow ID: mbpp_44_0
# Benchmark: mbpp
# Data Indices: [139]

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

        # Step 1: Initial Analysis
        analysis = await self.generate(
            instruction="""Extract the function name from the assert statements and analyze the task:
            - Identify the function name exactly as it appears in the assert statements.
            - Summarize the task requirements based on the natural language description.
            - Highlight any ambiguities or unclear aspects.""",
            context=""
        )

        # Step 2: Task Decomposition
        decomposition = await self.generate(
            instruction=f"""Break down the task into components:
            Based on the analysis: {analysis}
            - Identify input types and formats.
            - Describe the transformation or computation required.
            - Specify output types and formats.
            - List any constraints or edge cases.""",
            context=analysis
        )

        # Step 3: Parallel Code Generation
        candidates = await asyncio.gather(
            self.generate(
                instruction=f"""Generate a straightforward implementation:
                Based on the decomposition: {decomposition}
                - Use standard Python constructs.
                - Ensure the function name matches the assert statements.
                - Include necessary imports.""",
                context=decomposition
            ),
            self.generate(
                instruction=f"""Generate an alternative implementation:
                Based on the decomposition: {decomposition}
                - Explore using Python standard library functions.
                - Ensure the function name matches the assert statements.
                - Include necessary imports.""",
                context=decomposition
            ),
            self.generate(
                instruction=f"""Generate a minimalistic implementation:
                Based on the decomposition: {decomposition}
                - Focus on handling edge cases.
                - Ensure the function name matches the assert statements.
                - Include necessary imports.""",
                context=decomposition
            )
        )

        # Step 4: Ensemble Selection
        selected_solution = await self.ensemble(
            instruction="""Select the best candidate solution:
            Criteria:
            - Correctness: Must pass all test cases.
            - Simplicity: Prefer straightforward implementations.
            - Completeness: Handle all edge cases.""",
            contexts_list=candidates
        )

        # Step 5: Iterative Refinement
        refined_solution = selected_solution
        for _ in range(3):  # Allow up to 3 refinement iterations
            validation = await self.generate(
                instruction=f"""Validate the solution:
                Current solution: {refined_solution}
                - Check if it passes all test cases.
                - Identify any errors or missing details.""",
                context=refined_solution
            )
            if "error" in validation.lower() or "missing" in validation.lower():
                refined_solution = await self.revise(
                    instruction=f"""Refine the solution:
                    Issues identified: {validation}
                    - Fix errors.
                    - Add missing details.
                    - Ensure the function name matches the assert statements.""",
                    context=refined_solution
                )
            else:
                break

        return refined_solution