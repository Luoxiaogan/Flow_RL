# Workflow ID: mbpp_102_0
# Benchmark: mbpp
# Data Indices: [349]

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

        # Step 1: Extract function name
        function_name_context = await self.generate(
            instruction="Extract the function name from the assert statements. "
                        "The function name appears before the parentheses in the assert statements. "
                        "Return only the function name.",
            context=""
        )
        function_name = function_name_context.strip()

        # Step 2: Analyze task description
        task_analysis = await self.generate(
            instruction=f"Analyze the natural language task description. Identify the inputs, outputs, "
                        f"and any constraints. Use the function name '{function_name}' to guide your analysis.",
            context=""
        )

        # Step 3: Analyze test cases in parallel
        test_case_analysis = await asyncio.gather(
            self.generate(instruction="Identify input types and ranges from the test cases.", context=""),
            self.generate(instruction="Identify expected outputs from the test cases.", context=""),
            self.generate(instruction="Identify edge cases and special conditions from the test cases.", context="")
        )
        test_case_summary = "\n".join(test_case_analysis)

        # Step 4: Classify problem type
        problem_type = await self.generate(
            instruction=f"Classify the problem based on the task analysis and test case summary:\n"
                        f"Task Analysis: {task_analysis}\n"
                        f"Test Case Summary: {test_case_summary}\n"
                        f"Categories: Mathematical computation, String manipulation, Data structure operations, etc.",
            context=""
        )

        # Step 5: Generate initial code
        initial_code = await self.generate(
            instruction=f"Generate Python code for the function '{function_name}'. "
                        f"Follow these guidelines:\n"
                        f"- Include necessary imports at the top.\n"
                        f"- Use proper indentation (4 spaces).\n"
                        f"- Ensure the code satisfies the task description and test cases.\n"
                        f"Problem Type: {problem_type}",
            context=""
        )

        # Step 6: Validate and refine code iteratively
        max_iterations = 5
        code = initial_code
        for iteration in range(max_iterations):
            validation = await self.generate(
                instruction=f"Validate the code against the test cases. "
                            f"Identify any errors or mismatches. Return 'PASS' if all tests pass.",
                context=code
            )
            if "PASS" in validation:
                break
            code = await self.revise(
                instruction=f"Fix the following issues in the code:\n{validation}",
                context=code
            )

        # Step 7: Select final solution (if multiple candidates exist)
        final_code = await self.ensemble(
            instruction="Select the best solution based on correctness, efficiency, and readability.",
            contexts_list=[code]
        )

        return final_code