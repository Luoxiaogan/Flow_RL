# Workflow ID: mbpp_27_0
# Benchmark: mbpp
# Data Indices: [255, 84]

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
        # --- ALL IMPORTS MUST GO HERE INSIDE THE METHOD ---
        import asyncio

        # Stage 1: Initial Analysis
        initial_analysis = await self.generate(
            instruction="""Extract the function name from the test cases and summarize the task:
            - Identify the function name used in the assert statements
            - Summarize the task in one sentence
            - List key requirements and constraints""",
            context=""
        )
        refined_analysis = await self.revise(
            instruction="Ensure the function name and summary are accurate and complete.",
            context=initial_analysis
        )

        # Stage 2: Parallel Exploration
        explorations = await asyncio.gather(
            self.generate(
                instruction=f"""Analyze the problem from a mathematical perspective:
                {refined_analysis}
                Focus on formulas, computations, and logical steps.""",
                context=refined_analysis
            ),
            self.generate(
                instruction=f"""Analyze the problem from an algorithmic perspective:
                {refined_analysis}
                Focus on data structures, transformations, and procedural steps.""",
                context=refined_analysis
            ),
            self.generate(
                instruction=f"""Analyze the problem from a standard library usage perspective:
                {refined_analysis}
                Identify relevant Python modules and functions.""",
                context=refined_analysis
            )
        )
        refined_explorations = await asyncio.gather(
            *[self.revise(
                instruction="Refine the analysis for clarity and completeness.",
                context=exploration
            ) for exploration in explorations]
        )

        # Stage 3: Synthesis
        synthesis = await self.ensemble(
            instruction="""Combine insights from all analyses into a unified solution:
            - Use the function name extracted earlier
            - Include necessary imports
            - Ensure proper indentation and syntax
            - Address all requirements and constraints""",
            contexts_list=refined_explorations
        )

        # Stage 4: Validation and Iteration
        max_iterations = 3
        for iteration in range(max_iterations):
            validation = await self.generate(
                instruction=f"""Validate the generated code against the test cases:
                Code:
                {synthesis}
                
                Test Cases:
                {self.problem_text}
                
                Identify any errors or mismatches.""",
                context=synthesis
            )
            if "error" not in validation.lower():
                break  # Exit loop if validation passes
            synthesis = await self.revise(
                instruction=f"""Fix issues identified during validation:
                Issues:
                {validation}
                
                Correct the code and ensure it passes all test cases.""",
                context=synthesis
            )

        return synthesis