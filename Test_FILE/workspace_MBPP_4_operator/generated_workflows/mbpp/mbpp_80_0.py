# Workflow ID: mbpp_80_0
# Benchmark: mbpp
# Data Indices: [104]

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

        # Step 1: Extract function name and analyze task
        function_name_extraction = await self.generate(
            instruction="Extract the function name from the assert statements. "
                        "Focus on the left-hand side of the assertions. "
                        "Return only the function name.",
            context=""
        )

        task_analysis = await self.generate(
            instruction=f"Analyze the task description to understand the problem type, "
                        f"inputs, outputs, and operations. Function name: {function_name_extraction}. "
                        "Identify potential edge cases and required libraries.",
            context=""
        )

        # Step 2: Generate multiple solution candidates
        candidates = await asyncio.gather(
            self.generate(
                instruction=f"Generate a straightforward solution using basic Python constructs. "
                            f"Task analysis: {task_analysis}.",
                context=""
            ),
            self.generate(
                instruction=f"Generate an optimized solution using Python's standard library. "
                            f"Task analysis: {task_analysis}.",
                context=""
            ),
            self.generate(
                instruction=f"Generate a solution that explicitly handles edge cases. "
                            f"Task analysis: {task_analysis}.",
                context=""
            )
        )

        # Step 3: Validate and select best candidate
        validations = await asyncio.gather(
            *[self.generate(
                instruction=f"Validate this solution against the test cases. "
                            f"Solution: {candidate}. Task analysis: {task_analysis}.",
                context=candidate
            ) for candidate in candidates]
        )

        best_candidate = await self.ensemble(
            instruction="Select the best solution based on correctness, efficiency, and clarity. "
                        "Synthesize improvements if necessary.",
            contexts_list=validations
        )

        # Step 4: Finalize code
        final_code = await self.revise(
            instruction=f"Finalize the selected solution into clean, executable Python code. "
                        f"Ensure proper imports, indentation, and syntax. Add comments for clarity. "
                        f"Solution: {best_candidate}. Task analysis: {task_analysis}.",
            context=best_candidate
        )

        return final_code