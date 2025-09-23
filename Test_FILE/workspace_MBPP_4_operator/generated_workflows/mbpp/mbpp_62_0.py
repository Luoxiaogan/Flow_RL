# Workflow ID: mbpp_62_0
# Benchmark: mbpp
# Data Indices: [45]

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
        initial_analysis = await self.generate(
            instruction="""
Extract the following information from the problem:
1. Function name: Look for the name in the assert statements.
2. Task description: Summarize the natural language description into a concise problem statement.
3. Input types: Identify the types of inputs based on the test cases.
4. Output type: Infer the expected output type from the test cases.
5. Edge cases: Identify any edge cases hinted at by the test cases.
""",
            context=""
        )

        # Step 2: Parallel Exploration of Solution Approaches
        approaches = await asyncio.gather(
            self.generate(
                instruction="Develop a mathematical solution focusing on precise calculations.",
                context=initial_analysis
            ),
            self.generate(
                instruction="Develop a logical solution emphasizing algorithmic reasoning.",
                context=initial_analysis
            ),
            self.generate(
                instruction="Develop a practical solution leveraging Python's standard library.",
                context=initial_analysis
            )
        )

        # Step 3: Validation and Refinement
        for i, approach in enumerate(approaches):
            validation = await self.generate(
                instruction=f"Validate solution {i+1} against the test cases.",
                context=approach
            )
            if "error" in validation.lower():
                approaches[i] = await self.revise(
                    instruction=f"Fix issues: {validation}",
                    context=approach
                )

        # Step 4: Synthesis of Best Solution
        best_solution = await self.ensemble(
            instruction="Select the most complete, robust, and efficient solution.",
            contexts_list=approaches
        )

        return best_solution