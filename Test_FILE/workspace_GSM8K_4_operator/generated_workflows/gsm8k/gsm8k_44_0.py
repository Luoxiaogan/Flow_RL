# Workflow ID: gsm8k_44_0
# Benchmark: gsm8k
# Data Indices: [34, 37]

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

        # Step 1: Analyze the problem to classify its type and extract key information
        analysis = await self.generate(
            instruction="""Classify this problem:
            1. Is it numerical, logical, or textual?
            2. Does it require exact calculation or estimation?
            3. Are there multiple valid approaches?
            4. What's the expected answer format?
            Provide structured classification.""",
            context=""
        )

        # Step 2: Generate multiple solution attempts in parallel
        solution_attempts = await asyncio.gather(
            self.generate(
                instruction="Solve using sequential operations...",
                context=analysis
            ),
            self.generate(
                instruction="Solve using rate-based calculations...",
                context=analysis
            ),
            self.generate(
                instruction="Solve using distribution and proportions...",
                context=analysis
            )
        )

        # Step 3: Revise each attempt to verify calculations and enhance clarity
        revised_attempts = await asyncio.gather(
            *[self.revise(
                instruction="Verify calculations and enhance clarity...",
                context=attempt
            ) for attempt in solution_attempts]
        )

        # Step 4: Summarize the revised attempts to condense key points
        summarized_attempts = await asyncio.gather(
            *[self.summarize(
                instruction="Condense key points while preserving essential information...",
                context=attempt
            ) for attempt in revised_attempts]
        )

        # Step 5: Ensemble the summarized attempts to select the best solution
        best_solution = await self.ensemble(
            instruction="Select the most accurate and clear solution...",
            contexts_list=summarized_attempts
        )

        # Step 6: Iterate if necessary to refine the solution based on feedback
        for _ in range(2):  # Allow up to 2 iterations for refinement
            validation = await self.generate(
                instruction="Validate the solution and identify any errors...",
                context=best_solution
            )
            if "error" in validation.lower():
                best_solution = await self.revise(
                    instruction=f"Fix identified issues: {validation}",
                    context=best_solution
                )
            else:
                break

        return best_solution