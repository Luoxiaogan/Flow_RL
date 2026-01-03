# Workflow ID: mbpp_103_0
# Benchmark: mbpp
# Data Indices: [274, 185]

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

        # Step 1: Extract function name and analyze task description
        function_info = await self.generate(
            instruction="""Extract the function name and arguments from the test cases. 
            Analyze the task description to understand the problem requirements. 
            Provide a structured summary including:
            - Function name
            - Expected input types
            - Expected output type
            - Key operations described in the task""",
            context=""
        )

        # Step 2: Interpret test cases and infer patterns
        test_case_analysis = await self.generate(
            instruction="""Analyze the test cases to infer input/output patterns. 
            Identify edge cases and constraints. Provide a detailed breakdown of:
            - Input formats
            - Output formats
            - Any implicit assumptions or constraints""",
            context=function_info
        )

        # Step 3: Generate multiple solution strategies in parallel
        strategies = await asyncio.gather(
            self.generate(
                instruction="Generate a solution using list/array operations.",
                context=test_case_analysis
            ),
            self.generate(
                instruction="Generate a solution using mathematical computations.",
                context=test_case_analysis
            ),
            self.generate(
                instruction="Generate a solution using string manipulations.",
                context=test_case_analysis
            )
        )

        # Step 4: Select the best strategy
        best_strategy = await self.ensemble(
            instruction="""Evaluate the strategies based on clarity, efficiency, and alignment with the test cases. 
            Select the most promising approach.""",
            contexts_list=strategies
        )

        # Step 5: Generate and validate code
        code_draft = await self.generate(
            instruction=f"""Generate Python code for the selected strategy. 
            Ensure the function name matches the extracted name and the code adheres to Pythonic conventions. 
            Include necessary imports at the top of the code.""",
            context=best_strategy
        )

        for _ in range(3):  # Allow up to 3 refinement iterations
            validation = await self.generate(
                instruction=f"""Validate the generated code against the test cases. 
                Identify any errors or mismatches. Provide detailed feedback.""",
                context=code_draft
            )
            if "error" in validation.lower():
                code_draft = await self.revise(
                    instruction=f"""Fix the issues identified in the validation step: {validation}. 
                    Ensure the code passes all test cases.""",
                    context=code_draft
                )
            else:
                break

        # Step 6: Final refinement
        final_code = await self.revise(
            instruction="""Polish the code for readability and efficiency. 
            Ensure proper indentation, complete imports, and clean syntax.""",
            context=code_draft
        )

        return final_code