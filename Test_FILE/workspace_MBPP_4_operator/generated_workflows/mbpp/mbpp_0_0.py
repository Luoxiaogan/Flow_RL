# Workflow ID: mbpp_0_0
# Benchmark: mbpp
# Data Indices: [81, 62]

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

        # Step 1: Extract function name and arguments from assert statements
        func_extraction = await self.generate(
            instruction="""Extract the function name and arguments from the assert statements.
            Format the result as:
            Function Name: <name>
            Arguments: <arg1>, <arg2>, ...
            Ensure the function name matches exactly what appears in the assert statements.""",
            context=""
        )

        # Step 2: Analyze task description to infer required operation
        task_analysis = await self.generate(
            instruction=f"""Analyze the task description to determine the required operation.
            Based on the extracted function details:
            {func_extraction}
            
            Classify the problem type (e.g., list operation, mathematical computation).
            Map it to appropriate Python constructs and libraries.
            Identify potential edge cases based on the task description.""",
            context=func_extraction
        )

        # Step 3: Generate initial code solution
        initial_code = await self.generate(
            instruction=f"""Generate Python code for the function based on the analysis:
            {task_analysis}
            
            Include necessary imports, proper indentation, and handle edge cases.
            Ensure the function name matches the extracted name.
            Validate against the provided test cases.""",
            context=task_analysis
        )

        # Step 4: Parallel analysis of edge cases and validation
        validation, edge_cases = await asyncio.gather(
            self.generate(
                instruction=f"""Validate the generated code against the provided test cases:
                {initial_code}
                
                Report any failing test cases or errors.""",
                context=initial_code
            ),
            self.generate(
                instruction=f"""Identify additional edge cases not covered by the test cases:
                {task_analysis}
                
                Consider empty inputs, boundary conditions, and extreme values.""",
                context=task_analysis
            )
        )

        # Step 5: Conditional refinement loop
        refined_code = initial_code
        max_iterations = 3
        for _ in range(max_iterations):
            if "fail" not in validation.lower():
                break  # Exit loop if validation passes
            
            # Revise code based on validation feedback
            refined_code = await self.revise(
                instruction=f"""Revise the code to address validation issues:
                {validation}
                
                Incorporate additional edge cases:
                {edge_cases}
                
                Ensure the function remains consistent with the task description.""",
                context=refined_code
            )
            
            # Re-validate the revised code
            validation = await self.generate(
                instruction=f"""Re-validate the revised code:
                {refined_code}
                
                Report any remaining issues.""",
                context=refined_code
            )

        # Final Output
        return refined_code