# Workflow ID: mbpp_17_0
# Benchmark: mbpp
# Data Indices: [353, 64]

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

        # Step 1: Extract function name and analyze task description
        async def extract_function_name():
            return await self.generate(
                instruction="""Extract the function name from the assert statements.
                Ensure the name matches the format used in the test cases.
                If multiple names are possible, select the most consistent one.""",
                context=""
            )

        async def analyze_task():
            return await self.generate(
                instruction="""Analyze the task description to identify:
                - Inputs and their types
                - Expected outputs
                - Key transformations or operations
                - Any constraints or edge cases mentioned.""",
                context=""
            )

        func_name_result, task_analysis = await asyncio.gather(extract_function_name(), analyze_task())

        # Step 2: Parallel analysis from multiple perspectives
        perspectives = await asyncio.gather(
            self.generate(instruction="Analyze the problem mathematically.", context=task_analysis),
            self.generate(instruction="Analyze the problem logically.", context=task_analysis),
            self.generate(instruction="Analyze the problem textually.", context=task_analysis)
        )
        unified_analysis = await self.ensemble(
            instruction="Synthesize insights into a unified understanding.",
            contexts_list=perspectives
        )

        # Step 3: Conditional branching based on problem type
        problem_type = await self.generate(
            instruction="""Classify the problem into one of the following categories:
            - Numerical computation
            - String manipulation
            - Data structure transformation
            - Standard library usage
            Provide reasoning for the classification.""",
            context=unified_analysis
        )

        if "numerical" in problem_type.lower():
            solution_strategy = "Focus on mathematical operations and precision."
        elif "string" in problem_type.lower():
            solution_strategy = "Use string methods and pattern matching."
        elif "data structure" in problem_type.lower():
            solution_strategy = "Leverage list/dictionary operations and algorithms."
        else:
            solution_strategy = "Utilize Python's standard library functions."

        # Step 4: Generate and refine code iteratively
        async def generate_code():
            return await self.generate(
                instruction=f"""Generate Python code based on the following:
                Function name: {func_name_result}
                Task analysis: {task_analysis}
                Unified analysis: {unified_analysis}
                Solution strategy: {solution_strategy}
                Ensure the code includes necessary imports and adheres to Python syntax.""",
                context=""
            )

        async def validate_and_refine(code):
            validation = await self.generate(
                instruction=f"""Validate the generated code against test cases:
                - Does it pass all assert statements?
                - Are there any edge cases not handled?
                Provide feedback for improvement.""",
                context=code
            )
            if "error" in validation.lower():
                return await self.revise(
                    instruction=f"Fix issues: {validation}",
                    context=code
                )
            return code

        code = await generate_code()
        for _ in range(3):  # Allow up to 3 refinement iterations
            refined_code = await validate_and_refine(code)
            if refined_code == code:  # No further changes needed
                break
            code = refined_code

        # Step 5: Final synthesis and output
        final_code = await self.summarize(
            instruction="Condense the final solution into a clean, executable Python code block.",
            context=code
        )

        return final_code