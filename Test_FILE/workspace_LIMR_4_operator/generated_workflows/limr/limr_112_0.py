# Workflow ID: limr_112_0
# Benchmark: limr
# Data Indices: [21, 239]

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

        # Initial Analysis: Classify problem and extract key information
        initial_analysis = await self.generate(
            instruction="""Analyze the problem:
            - Identify the mathematical domain (geometry, number theory, etc.)
            - Extract key variables, constraints, and relationships
            - Determine the expected answer format (integer, equation, etc.)
            - Suggest potential solution strategies""",
            context=""
        )

        # Parallel Exploration: Generate multiple solution attempts
        solution_attempts = await asyncio.gather(
            self.generate(
                instruction=f"""Solve using algebraic methods:
                - Perform symbolic manipulation
                - Solve equations step-by-step
                - Validate intermediate results""",
                context=initial_analysis
            ),
            self.generate(
                instruction=f"""Solve using geometric reasoning:
                - Visualize shapes and relationships
                - Apply coordinate geometry or trigonometry
                - Verify calculations""",
                context=initial_analysis
            ),
            self.generate(
                instruction=f"""Solve using combinatorial techniques:
                - Count possibilities systematically
                - Apply probability principles
                - Check consistency of results""",
                context=initial_analysis
            )
        )

        # Validation and Refinement: Improve each solution attempt
        refined_solutions = await asyncio.gather(
            *[self.revise(
                instruction=f"""Refine the solution:
                - Correct errors in calculations
                - Add missing steps or explanations
                - Ensure logical consistency""",
                context=solution
            ) for solution in solution_attempts]
        )

        # Final Synthesis: Select or combine the best solution
        final_solution = await self.ensemble(
            instruction="""Evaluate all solutions:
            - Check for correctness and completeness
            - Select the most elegant or efficient approach
            - Combine insights if necessary
            - Present the final answer in the required format""",
            contexts_list=refined_solutions
        )

        return final_solution