# Workflow ID: gsm8k_70_0
# Benchmark: gsm8k
# Data Indices: [263, 95]

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
            instruction="""Classify the problem type:
            - Is it numerical, rate, distribution, proportion, or multi-entity?
            - Identify key entities, numbers, relationships, and constraints.
            - What is being asked for?""",
            context=""
        )

        # Step 2: Parallel Solution Generation
        solution_paths = await asyncio.gather(
            self.generate(
                instruction=f"""Solve using precise numerical computation:
                - Show all algebraic steps.
                - Maintain full precision.
                - Double-check arithmetic.""",
                context=initial_analysis
            ),
            self.generate(
                instruction=f"""Solve using rate-based reasoning:
                - Focus on dimensional analysis and unit consistency.
                - Handle time, speed, and distance relationships.""",
                context=initial_analysis
            ),
            self.generate(
                instruction=f"""Solve using distribution logic:
                - Handle divisions and remainders.
                - Ensure equal sharing where applicable.""",
                context=initial_analysis
            ),
            self.generate(
                instruction=f"""Solve using proportional reasoning:
                - Scale values appropriately.
                - Handle percentages, fractions, and ratios.""",
                context=initial_analysis
            ),
            self.generate(
                instruction=f"""Solve using multi-entity tracking:
                - Track quantities for each entity separately.
                - Manage interdependencies carefully.""",
                context=initial_analysis
            )
        )

        # Step 3: Intermediate Validation
        validations = await asyncio.gather(
            *[self.generate(
                instruction=f"Validate this solution path for logical consistency and numerical correctness.",
                context=path
            ) for path in solution_paths]
        )

        # Step 4: Iterative Refinement
        refined_paths = []
        for path, validation in zip(solution_paths, validations):
            if "error" in validation.lower():
                refined = await self.revise(
                    instruction=f"Correct errors identified in validation: {validation}",
                    context=path
                )
                refined_paths.append(refined)
            else:
                refined_paths.append(path)

        # Step 5: Synthesis and Final Answer
        final_answer = await self.ensemble(
            instruction="Select the best solution path or synthesize results from multiple paths.",
            contexts_list=refined_paths
        )

        return final_answer