# Workflow ID: limr_9_0
# Benchmark: limr
# Data Indices: [17, 57]

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

        # Initial Analysis: Classify the problem and extract key information
        initial_analysis = await self.generate(
            instruction="""Classify this problem:
            1. Is it numerical, logical, or textual?
            2. Does it require exact calculation or estimation?
            3. Are there multiple valid approaches?
            4. What's the expected answer format?
            Provide structured classification.""",
            context=""
        )

        # Parallel Exploration: Generate multiple solution attempts
        solution_attempts = await asyncio.gather(
            self.generate(
                instruction="Solve using algebraic methods...",
                context=initial_analysis
            ),
            self.generate(
                instruction="Solve using geometric methods...",
                context=initial_analysis
            ),
            self.generate(
                instruction="Solve using combinatorial methods...",
                context=initial_analysis
            )
        )

        # Validation and Refinement: Improve each solution attempt
        refined_solutions = await asyncio.gather(
            *[self.revise(
                instruction=f"Validate and refine solution: {solution}",
                context=solution
            ) for solution in solution_attempts]
        )

        # Ensemble Decision: Select the best solution
        final_solution = await self.ensemble(
            instruction="Select the most accurate and complete solution.",
            contexts_list=refined_solutions
        )

        # Final Verification: Ensure the solution meets all constraints
        verified_solution = await self.revise(
            instruction="Verify the final solution against all constraints and requirements.",
            context=final_solution
        )

        return verified_solution