# Workflow ID: mbpp_106_0
# Benchmark: mbpp
# Data Indices: [253]

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

        # Step 1: Extract function name and key components
        analysis = await self.generate(
            instruction="""Extract the function name from the assert statements and identify key components:
            - Function name (e.g., 'raw_heap')
            - Input types (e.g., list of integers)
            - Output type (e.g., transformed list)
            - Key operations described in the task (e.g., 'convert to a heap')""",
            context=""
        )

        # Parse function name using regex
        function_name_match = re.search(r"assert (\w+)\(", self.problem_text)
        function_name = function_name_match.group(1) if function_name_match else "unknown_function"

        # Step 2: Generate multiple interpretations of the task
        interpretations = await asyncio.gather(
            self.generate(
                instruction=f"""Interpret the task as a list transformation:
                - Describe the input-output mapping
                - Identify required Python modules (e.g., heapq)""",
                context=analysis
            ),
            self.generate(
                instruction=f"""Interpret the task as a mathematical computation:
                - Describe any numerical transformations
                - Identify required algorithms or formulas""",
                context=analysis
            )
        )

        # Step 3: Synthesize interpretations into a unified strategy
        strategy = await self.ensemble(
            instruction="""Synthesize interpretations into a single solution strategy:
            - Select the most relevant interpretation
            - Combine insights from both interpretations if necessary""",
            contexts_list=interpretations
        )

        # Step 4: Generate initial code draft
        code_draft = await self.generate(
            instruction=f"""Generate Python code based on the solution strategy:
            - Include necessary imports at the top
            - Define the function '{function_name}'
            - Implement the described operations
            - Ensure proper indentation and syntax""",
            context=strategy
        )

        # Step 5: Refine code for correctness and clarity
        refined_code = await self.revise(
            instruction=f"""Refine the generated code:
            - Fix any syntax errors
            - Ensure compliance with Python standards
            - Add comments explaining key steps""",
            context=code_draft
        )

        # Step 6: Validate code against test cases
        validation = await self.generate(
            instruction=f"""Validate the code against the provided test cases:
            - Simulate the test cases
            - Check if all assertions pass
            - Identify any discrepancies""",
            context=refined_code
        )

        # Step 7: Iteratively refine until all test cases pass
        for _ in range(3):  # Limit iterations to avoid infinite loops
            if "error" in validation.lower():
                refined_code = await self.revise(
                    instruction=f"""Fix issues identified during validation:
                    - Address specific errors mentioned in the feedback
                    - Re-test the code""",
                    context=refined_code
                )
                validation = await self.generate(
                    instruction="Re-validate the code against test cases",
                    context=refined_code
                )
            else:
                break

        return refined_code