# Workflow ID: mbpp_94_0
# Benchmark: mbpp
# Data Indices: [303]

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

        # Step 1: Extract function name and input/output patterns
        func_analysis = await self.generate(
            instruction="""Extract the function name and input/output patterns from the test cases:
            - Look for 'assert' statements.
            - Identify the function name and its arguments.
            - Infer the expected output format.
            Provide structured output:""",
            context=""
        )

        # Step 2: Analyze task description
        task_analysis = await self.generate(
            instruction="""Analyze the task description:
            - Identify key operations (e.g., mathematical, string manipulation).
            - Detect implicit constraints or edge cases.
            - Summarize the required logic.
            Provide structured output:""",
            context=""
        )

        # Step 3: Generate candidate solutions
        candidates = await asyncio.gather(
            self.generate(
                instruction=f"""Generate a solution based on:
                Function Analysis: {func_analysis}
                Task Analysis: {task_analysis}
                Ensure the solution passes all test cases.""",
                context=""
            ),
            self.generate(
                instruction=f"""Generate an alternative solution based on:
                Function Analysis: {func_analysis}
                Task Analysis: {task_analysis}
                Focus on edge cases and constraints.""",
                context=""
            )
        )

        # Step 4: Validate and refine
        validated_solutions = []
        for candidate in candidates:
            for _ in range(3):  # Allow up to 3 refinement iterations
                validation = await self.generate(
                    instruction=f"""Validate the solution against test cases:
                    Solution: {candidate}
                    Report any errors or mismatches.""",
                    context=""
                )
                if "error" in validation.lower():
                    candidate = await self.revise(
                        instruction=f"""Revise the solution to fix:
                        Validation Feedback: {validation}""",
                        context=candidate
                    )
                else:
                    validated_solutions.append(candidate)
                    break

        # Step 5: Synthesize final solution
        final_solution = await self.ensemble(
            instruction="""Select the best solution:
            Criteria:
            - Correctness: Passes all test cases.
            - Simplicity: Minimal and readable code.
            - Pythonic: Follows conventions and best practices.""",
            contexts_list=validated_solutions
        )

        return final_solution