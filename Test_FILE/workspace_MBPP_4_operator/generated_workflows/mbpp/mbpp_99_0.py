# Workflow ID: mbpp_99_0
# Benchmark: mbpp
# Data Indices: [187, 201]

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

        # Step 1: Initial Analysis
        analysis = await self.generate(
            instruction="""Extract key components from the problem:
            - Task description: What does the function do?
            - Function name: Extract from assert statements.
            - Input types and output format: Infer from test cases.
            Provide structured output.""",
            context=""
        )

        # Step 2: Parallel Exploration of Solution Strategies
        direct_translation, pattern_matching, std_lib_usage = await asyncio.gather(
            self.generate(
                instruction="Translate the task description directly into Python code.",
                context=analysis
            ),
            self.generate(
                instruction="Identify common patterns (e.g., loops, comprehensions) and implement them.",
                context=analysis
            ),
            self.generate(
                instruction="Leverage Python's standard library functions to solve the problem.",
                context=analysis
            )
        )

        # Step 3: Conditional Branching Based on Problem Type
        strategy = await self.ensemble(
            instruction="""Select the best strategy based on the problem type:
            - Numerical problems: Prefer mathematical precision.
            - String manipulation: Focus on pattern matching.
            - Data structures: Use standard library functions.""",
            contexts_list=[direct_translation, pattern_matching, std_lib_usage]
        )

        # Step 4: Iterative Refinement
        refined_code = strategy
        for _ in range(3):  # Allow up to 3 refinement iterations
            validation = await self.generate(
                instruction="Validate the code against the test cases and identify issues.",
                context=refined_code
            )
            if "error" in validation.lower():
                refined_code = await self.revise(
                    instruction=f"Fix issues: {validation}",
                    context=refined_code
                )
            else:
                break

        # Step 5: Final Validation
        final_code = await self.revise(
            instruction="Ensure the code is complete, includes all necessary imports, and passes all test cases.",
            context=refined_code
        )

        return final_code