# Workflow ID: mbpp_18_0
# Benchmark: mbpp
# Data Indices: [226]

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

        # Step 1: Analyze the problem to extract key information
        analysis = await self.generate(
            instruction="""Analyze the problem:
            1. Extract the function name from the assert statements.
            2. Identify the input types and their roles (e.g., list, integer, string).
            3. Infer the expected behavior from the task description.
            Format the output as structured information.""",
            context=""
        )

        # Step 2: Generate initial code based on the analysis
        initial_code = await self.generate(
            instruction=f"""Write Python code for the function identified in the analysis:
            - Takes inputs of type [input_types].
            - Implements the behavior described in the task.
            - Includes necessary imports.
            Analysis: {analysis}""",
            context=analysis
        )

        # Step 3: Validate the initial code against test cases
        validation = await self.generate(
            instruction=f"""Validate the code against the test cases:
            1. Check if all assertions pass.
            2. Identify any missing edge cases or logical errors.
            3. Suggest improvements for clarity and correctness.
            Code: {initial_code}""",
            context=initial_code
        )

        # Step 4: Revise the code based on validation feedback
        revised_code = await self.revise(
            instruction=f"""Revise the code to address issues identified during validation:
            - Fix logical errors.
            - Handle edge cases.
            - Improve clarity and efficiency.
            Validation Feedback: {validation}
            Original Code: {initial_code}""",
            context=initial_code
        )

        # Step 5: Ensemble multiple attempts if necessary
        final_code = await self.ensemble(
            instruction="""Select the most accurate and efficient version of the code:
            - Consider correctness, clarity, and adherence to test cases.
            - Merge complementary improvements from different versions.""",
            contexts_list=[initial_code, revised_code]
        )

        return final_code