# Workflow ID: mbpp_33_0
# Benchmark: mbpp
# Data Indices: [59]

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

        # Step 1: Initial Analysis
        initial_analysis = await self.generate(
            instruction="""Extract the following information from the problem:
            1. Function name from assert statements.
            2. Key components of the task description.
            3. Input types and expected outputs from test cases.
            Provide structured output.""",
            context=""
        )

        # Step 2: Parallel Fork for Problem Understanding
        description_analysis = self.generate(
            instruction="Interpret the natural language task description and map it to programming constructs.",
            context=initial_analysis
        )
        test_case_analysis = self.generate(
            instruction="Analyze the test cases to infer input-output relationships and constraints.",
            context=initial_analysis
        )
        edge_case_identification = self.generate(
            instruction="Identify potential edge cases based on the task description and test cases.",
            context=initial_analysis
        )

        # Run analyses in parallel
        analyses = await asyncio.gather(description_analysis, test_case_analysis, edge_case_identification)
        synthesized_understanding = await self.ensemble(
            instruction="Synthesize the analyses into a unified understanding of the problem.",
            contexts_list=analyses
        )

        # Step 3: Code Generation
        code_attempt = await self.generate(
            instruction=f"""Generate Python code based on the following:
            {synthesized_understanding}
            
            Ensure the code:
            - Includes all necessary imports.
            - Uses the correct function name.
            - Handles edge cases.
            - Passes all test cases.""",
            context=synthesized_understanding
        )

        # Step 4: Validation and Iterative Refinement
        max_iterations = 3
        for iteration in range(max_iterations):
            validation = await self.generate(
                instruction=f"Validate the generated code against the test cases. Report any failures.",
                context=code_attempt
            )
            if "fail" not in validation.lower():
                break  # All test cases pass
            code_attempt = await self.revise(
                instruction=f"Refine the code to address the following issues: {validation}",
                context=code_attempt
            )

        return code_attempt