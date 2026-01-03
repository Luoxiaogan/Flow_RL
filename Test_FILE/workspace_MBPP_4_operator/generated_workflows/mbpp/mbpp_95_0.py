# Workflow ID: mbpp_95_0
# Benchmark: mbpp
# Data Indices: [233, 130]

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

        # Step 1: Problem Analysis
        analysis = await self.generate(
            instruction="""Analyze the problem:
            - Classify the problem type (e.g., mathematical, list manipulation).
            - Extract key entities (e.g., variables, constants).
            - Identify the function name from test cases.
            - Infer input types and expected outputs.""",
            context=""
        )

        # Step 2: Function Specification
        function_spec = await self.summarize(
            instruction="""Condense the analysis into a structured format:
            - Function name
            - Input types
            - Expected outputs
            - Key requirements""",
            context=analysis
        )

        # Step 3: Initial Code Generation
        initial_code = await self.generate(
            instruction=f"""Generate Python code based on the function specification:
            {function_spec}
            - Include necessary imports.
            - Follow Python conventions (indentation, naming).
            - Handle basic cases.""",
            context=function_spec
        )

        # Step 4: Validation and Refinement
        validation_results = await self.generate(
            instruction=f"""Validate the generated code against test cases:
            {initial_code}
            - Check for syntax errors.
            - Verify outputs match expected results.
            - Identify issues.""",
            context=initial_code
        )

        if "error" in validation_results.lower():
            refined_code = await self.revise(
                instruction=f"""Refine the code to fix issues:
                {validation_results}
                - Correct logical errors.
                - Improve clarity.
                - Ensure correctness.""",
                context=initial_code
            )
        else:
            refined_code = initial_code

        # Step 5: Edge Case Handling
        edge_cases = await self.generate(
            instruction=f"""Identify potential edge cases:
            {refined_code}
            - Invalid inputs (e.g., negative numbers).
            - Boundary conditions.
            - Special scenarios.""",
            context=refined_code
        )

        final_code = await self.revise(
            instruction=f"""Update the code to handle edge cases:
            {edge_cases}
            - Add checks for invalid inputs.
            - Ensure robustness.""",
            context=refined_code
        )

        return final_code