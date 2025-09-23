# Workflow ID: mbpp_116_0
# Benchmark: mbpp
# Data Indices: [347]

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

        # Step 1: Extract function name and interpret task description
        initial_analysis = await self.generate(
            instruction="""Extract the function name from the test cases and summarize the task description.
            - Identify patterns like 'assert function_name(...)' to extract the function name.
            - Analyze the natural language description to understand the task requirements.
            - Note any edge cases or constraints implied by the description.""",
            context=""
        )

        # Step 2: Condense analysis into structured format
        structured_analysis = await self.summarize(
            instruction="Condense the analysis into a clear, structured format.",
            context=initial_analysis
        )

        # Step 3: Explore multiple solution strategies in parallel
        strategies = await asyncio.gather(
            self.generate(
                instruction=f"""Generate a solution using direct indexing:
                {structured_analysis}""",
                context=""
            ),
            self.generate(
                instruction=f"""Generate a solution using iteration:
                {structured_analysis}""",
                context=""
            ),
            self.generate(
                instruction=f"""Generate a solution using slicing:
                {structured_analysis}""",
                context=""
            )
        )

        # Step 4: Select the best strategy
        best_strategy = await self.ensemble(
            instruction="Select the most promising strategy based on clarity, efficiency, and alignment with test cases.",
            contexts_list=strategies
        )

        # Step 5: Generate initial code
        initial_code = await self.generate(
            instruction=f"""Generate Python code for the selected strategy:
            {best_strategy}
            Ensure proper indentation, include necessary imports, and adhere to formatting rules.""",
            context=""
        )

        # Step 6: Validate and refine code
        refined_code = initial_code
        for _ in range(3):  # Allow up to 3 refinement iterations
            validation = await self.generate(
                instruction=f"""Validate the code against the test cases:
                Code: {refined_code}
                Identify any errors or mismatches.""",
                context=""
            )
            if "error" in validation.lower():
                refined_code = await self.revise(
                    instruction=f"""Fix issues in the code:
                    Issues: {validation}
                    Code: {refined_code}""",
                    context=refined_code
                )
            else:
                break

        # Step 7: Return final code
        return refined_code