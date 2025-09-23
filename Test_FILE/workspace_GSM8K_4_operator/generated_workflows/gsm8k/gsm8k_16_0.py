# Workflow ID: gsm8k_16_0
# Benchmark: gsm8k
# Data Indices: [133, 23]

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
            instruction="""Extract all numerical values, relationships, and the question being asked.
            Classify the problem type (e.g., sequential operations, proportions, rate problems).
            Format as structured information.""",
            context=""
        )

        # Step 2: Parallel Exploration
        strategies = [
            "Solve using direct sequential operations.",
            "Solve using proportional reasoning.",
            "Solve using rate-based calculations."
        ]
        solutions = await asyncio.gather(
            *[self.generate(instruction=f"Attempt solution using {strategy}", context=initial_analysis) 
              for strategy in strategies]
        )

        # Step 3: Validation and Refinement
        refined_solutions = []
        for solution in solutions:
            validation = await self.revise(
                instruction="Validate calculations and logical flow. Correct any errors.",
                context=solution
            )
            refined_solutions.append(validation)

        # Step 4: Ensemble Decision
        final_solution = await self.ensemble(
            instruction="Synthesize the best solution from the refined attempts. Ensure numerical precision and logical consistency.",
            contexts_list=refined_solutions
        )

        # Step 5: Final Output
        final_answer = await self.generate(
            instruction="Extract the final numerical answer from the solution. Return only the number.",
            context=final_solution
        )

        return final_answer.strip()