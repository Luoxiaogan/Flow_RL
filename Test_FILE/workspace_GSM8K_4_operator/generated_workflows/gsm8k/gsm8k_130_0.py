# Workflow ID: gsm8k_130_0
# Benchmark: gsm8k
# Data Indices: [81, 158]

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

        # Step 1: Analyze the problem
        analysis = await self.generate(
            instruction="""Analyze the problem:
            - Extract all numerical values and their context.
            - Identify relationships (e.g., rates, proportions).
            - Classify the problem type (sequential, proportional, rate-based, etc.).
            - Determine the question's goal and expected answer format.
            Provide a structured summary.""",
            context=""
        )

        # Step 2: Select solution strategy
        if "proportional" in analysis.lower():
            strategy = "proportional"
        elif "rate" in analysis.lower():
            strategy = "rate"
        else:
            strategy = "sequential"

        # Step 3: Solve sub-problems in parallel
        if strategy == "proportional":
            sub_solutions = await asyncio.gather(
                self.generate(instruction="Solve proportional relationships...", context=analysis),
                self.generate(instruction="Scale quantities as needed...", context=analysis)
            )
        elif strategy == "rate":
            sub_solutions = await asyncio.gather(
                self.generate(instruction="Calculate rates...", context=analysis),
                self.generate(instruction="Apply time-distance relationships...", context=analysis)
            )
        else:
            sub_solutions = await asyncio.gather(
                self.generate(instruction="Perform step-by-step calculations...", context=analysis)
            )

        # Step 4: Iterative refinement
        refined_solution = sub_solutions[0]
        for _ in range(3):  # Limit iterations to prevent infinite loops
            refined_solution = await self.revise(
                instruction="Improve clarity, fix errors, and ensure logical consistency...",
                context=refined_solution
            )

        # Step 5: Final synthesis and validation
        final_answer = await self.ensemble(
            instruction="Synthesize all results into a final numerical answer...",
            contexts_list=sub_solutions + [refined_solution]
        )

        return final_answer