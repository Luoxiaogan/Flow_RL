# Workflow ID: mbpp_90_0
# Benchmark: mbpp
# Data Indices: [140, 191]

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

        # Step 1: Extract function name and test cases
        extraction = await self.generate(
            instruction="""Extract the function name and test cases from the problem text:
            - Identify the function name from assert statements.
            - Parse the input arguments and expected outputs from test cases.
            Provide structured output in the format:
            Function Name: [name]
            Test Cases: [(input1, output1), (input2, output2), ...]""",
            context=""
        )

        # Step 2: Interpret task description
        task_interpretation = await self.generate(
            instruction=f"""Analyze the task description to understand the requirements:
            Problem Text: {self.problem_text}
            Extracted Information: {extraction}
            
            Provide a detailed interpretation of the task, including:
            - Input format and constraints
            - Output format and constraints
            - Key operations required
            - Potential edge cases""",
            context=extraction
        )

        # Step 3: Generate initial code
        initial_code = await self.generate(
            instruction=f"""Generate Python code based on the task interpretation:
            Task Interpretation: {task_interpretation}
            
            Ensure the code:
            - Uses the correct function name
            - Handles all input/output pairs from test cases
            - Includes necessary imports
            - Follows proper indentation and syntax""",
            context=task_interpretation
        )

        # Step 4: Validate code against test cases
        validation = await self.generate(
            instruction=f"""Validate the generated code against test cases:
            Generated Code: {initial_code}
            Test Cases: {extraction}
            
            Provide feedback on:
            - Which test cases pass
            - Which test cases fail and why
            - Any missing edge cases""",
            context=initial_code
        )

        # Step 5: Iterative refinement
        refined_code = initial_code
        for _ in range(3):  # Limit iterations to avoid excessive refinement
            if "fail" in validation.lower():
                refined_code = await self.revise(
                    instruction=f"""Revise the code based on validation feedback:
                    Current Code: {refined_code}
                    Validation Feedback: {validation}
                    
                    Fix issues and improve clarity while maintaining correctness.""",
                    context=refined_code
                )
                validation = await self.generate(
                    instruction=f"""Re-validate the revised code:
                    Revised Code: {refined_code}
                    Test Cases: {extraction}""",
                    context=refined_code
                )
            else:
                break

        # Step 6: Synthesize final solution
        final_solution = await self.ensemble(
            instruction="""Select the best solution from available candidates:
            Consider:
            - Correctness (passes all test cases)
            - Clarity (easy to understand)
            - Efficiency (minimal unnecessary computation)
            - Robustness (handles edge cases)""",
            contexts_list=[initial_code, refined_code]
        )

        return final_solution