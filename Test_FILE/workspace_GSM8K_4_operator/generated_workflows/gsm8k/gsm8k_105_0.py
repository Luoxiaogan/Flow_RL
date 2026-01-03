# Workflow ID: gsm8k_105_0
# Benchmark: gsm8k
# Data Indices: [14, 111]

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

        # Step 1: Initial Analysis - Extract entities and classify problem type
        initial_analysis = await self.generate(
            instruction="""Analyze the problem:
            - Extract all numbers, units, and relationships.
            - Classify the problem type (e.g., rate, proportion, distribution).
            - Identify explicit and implicit constraints.
            Provide structured output.""",
            context=""
        )

        # Step 2: Parallel Exploration - Generate multiple solution paths
        solution_paths = await asyncio.gather(
            self.generate(
                instruction=f"""Solve using direct calculation:
                - Follow the logical sequence of steps.
                - Show all intermediate results.
                - Ensure calculations are precise.""",
                context=initial_analysis
            ),
            self.generate(
                instruction=f"""Solve using estimation:
                - Approximate key values where appropriate.
                - Validate estimates against known constraints.""",
                context=initial_analysis
            ),
            self.generate(
                instruction=f"""Solve using logical reasoning:
                - Focus on relationships and implications.
                - Derive the solution step-by-step.""",
                context=initial_analysis
            )
        )

        # Step 3: Validation - Check each solution path for correctness
        validations = await asyncio.gather(
            *[self.revise(
                instruction="Verify correctness of calculations and logic.",
                context=path
            ) for path in solution_paths]
        )

        # Step 4: Synthesis - Select the most promising solution
        final_solution = await self.ensemble(
            instruction="""Synthesize insights from multiple paths:
            - Prioritize precise calculations over estimations.
            - Resolve conflicts between paths.
            - Ensure the final solution satisfies all constraints.""",
            contexts_list=validations
        )

        # Step 5: Finalization - Extract the numerical answer
        final_answer = await self.summarize(
            instruction="""Extract the final numerical answer:
            - Discard intermediate explanations.
            - Present only the single numerical value.""",
            context=final_solution
        )

        return final_answer.strip()