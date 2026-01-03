# Workflow ID: mbpp_16_0
# Benchmark: mbpp
# Data Indices: [206, 132]

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
            instruction="""Extract key information:
            - Function name from assert statements
            - Input types and expected output format
            - Problem type (e.g., list operation, math computation)
            Provide structured output.""",
            context=""
        )

        # Step 2: Parallel Code Generation
        candidates = await asyncio.gather(
            self.generate(
                instruction=f"""Generate Python code for the task:
                - Use function name and inputs from analysis: {analysis}
                - Interpret task literally""",
                context=analysis
            ),
            self.generate(
                instruction=f"""Generate Python code for the task:
                - Use function name and inputs from analysis: {analysis}
                - Interpret task broadly, considering edge cases""",
                context=analysis
            )
        )

        # Step 3: Validation
        validation_results = await asyncio.gather(
            *[self.generate(
                instruction=f"""Validate this code against test cases:
                Code: {candidate}
                Test cases: {self.problem_text}
                Return 'pass' if all test cases pass, otherwise describe failures.""",
                context=candidate
            ) for candidate in candidates]
        )

        # Step 4: Ensemble Selection
        selected_code = await self.ensemble(
            instruction="Select the best solution that passes all test cases.",
            contexts_list=validation_results
        )

        # Step 5: Refinement (if needed)
        if "fail" in selected_code.lower():
            refined_code = await self.revise(
                instruction=f"""Fix issues in this code:
                Code: {selected_code}
                Issues: {selected_code}
                Ensure it passes all test cases.""",
                context=selected_code
            )
            selected_code = refined_code

        # Final Output
        return selected_code