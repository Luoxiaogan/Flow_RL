# Workflow ID: mbpp_107_0
# Benchmark: mbpp
# Data Indices: [231]

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

        # Step 1: Extract function name and high-level task description
        initial_analysis = await self.generate(
            instruction="""Extract the function name from the test cases and summarize the task description.
            Include:
            - Function name
            - Input types
            - Expected output
            - Key operations""",
            context=""
        )

        # Step 2: Parallel exploration of task details and test case analysis
        task_details = await self.generate(
            instruction="Analyze the task description to identify detailed requirements and constraints.",
            context=initial_analysis
        )
        test_case_analysis = await self.generate(
            instruction="Analyze the test cases to infer expected behavior and edge cases.",
            context=initial_analysis
        )

        # Merge insights from both paths
        unified_understanding = await self.ensemble(
            instruction="Combine task details and test case analysis into a unified understanding.",
            contexts_list=[task_details, test_case_analysis]
        )

        # Step 3: Generate initial code
        initial_code = await self.generate(
            instruction=f"""Generate Python code based on the unified understanding:
            Unified Understanding: {unified_understanding}
            
            Ensure:
            - Proper function name
            - Correct imports
            - Clear logic
            - Handle edge cases""",
            context=unified_understanding
        )

        # Step 4: Iterative validation and refinement
        code = initial_code
        for _ in range(3):  # Allow up to 3 refinement iterations
            validation = await self.generate(
                instruction=f"Validate the code against the test cases:\n{code}",
                context=unified_understanding
            )
            if "error" in validation.lower():
                code = await self.revise(
                    instruction=f"Fix issues identified during validation:\n{validation}",
                    context=code
                )
            else:
                break

        # Step 5: Final output
        return f"