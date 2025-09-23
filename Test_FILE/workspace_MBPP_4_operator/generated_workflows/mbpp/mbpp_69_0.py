# Workflow ID: mbpp_69_0
# Benchmark: mbpp
# Data Indices: [7]

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

        # Step 1: Parallel Extraction and Analysis
        extraction_task = self.generate(
            instruction="""Extract the function name and signature from the test cases.
            Look for patterns like 'assert <function_name>(<args>) == <output>'.
            Return the function name and its expected arguments.""",
            context=""
        )
        analysis_task = self.generate(
            instruction="""Analyze the task description to identify key requirements, constraints, and potential edge cases.
            Consider input types, output format, and any special conditions mentioned in the description.""",
            context=""
        )
        extracted_info, analysis = await asyncio.gather(extraction_task, analysis_task)

        # Step 2: Generate Initial Code
        initial_code = await self.generate(
            instruction=f"""Generate Python code based on the following information:
            Function Name and Signature: {extracted_info}
            Task Analysis: {analysis}
            Ensure the code includes all necessary imports and follows proper indentation.""",
            context=""
        )

        # Step 3: Validate and Refine Code
        refined_code = initial_code
        for _ in range(3):  # Allow up to 3 refinement iterations
            validation = await self.revise(
                instruction=f"""Validate the code against the test cases.
                Identify any errors, inefficiencies, or missing edge cases.
                Provide specific feedback for improvement.""",
                context=refined_code
            )
            if "error" not in validation.lower():
                break  # Stop if no errors are found
            refined_code = await self.revise(
                instruction=f"""Refine the code based on the following feedback:
                {validation}
                Ensure all test cases pass and the code is clear and efficient.""",
                context=refined_code
            )

        # Step 4: Handle Edge Cases
        edge_cases = await self.generate(
            instruction=f"""Hypothesize additional edge cases based on the task analysis:
            {analysis}
            Consider extreme inputs, unexpected data types, and boundary conditions.""",
            context=""
        )
        final_code = await self.revise(
            instruction=f"""Ensure the code handles the following edge cases:
            {edge_cases}
            Make any necessary adjustments to the logic.""",
            context=refined_code
        )

        # Step 5: Final Synthesis
        solution = await self.ensemble(
            instruction="""Synthesize the refined code and any additional insights into a final solution.
            Ensure the code is complete, executable, and satisfies all test cases.""",
            contexts_list=[final_code, edge_cases]
        )

        return solution