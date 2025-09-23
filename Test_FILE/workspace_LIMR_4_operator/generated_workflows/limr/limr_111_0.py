# Workflow ID: limr_111_0
# Benchmark: limr
# Data Indices: [250, 241]

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
            instruction="Analyze the problem structure, identify key variables, constraints, and relationships. "
                        "Classify the problem type (e.g., geometry, number theory) and suggest possible solution approaches.",
            context=""
        )

        # Step 2: Parallel Solution Attempts
        approaches = ["algebraic manipulation", "combinatorial arguments", "geometric analysis", "number theory techniques"]
        solution_attempts = await asyncio.gather(
            *[self.generate(
                instruction=f"Solve the problem using {approach}. Show all steps and maintain full precision.",
                context=initial_analysis
            ) for approach in approaches]
        )

        # Step 3: Refinement and Validation
        refined_solutions = []
        for attempt in solution_attempts:
            refined = await self.revise(
                instruction="Improve clarity, add missing details, and verify calculations. "
                            "Correct any logical inconsistencies or mathematical errors.",
                context=attempt
            )
            refined_solutions.append(refined)

        # Step 4: Ensemble Decision Making
        best_solution = await self.ensemble(
            instruction="Compare the refined solutions, assess their validity and completeness, "
                        "and select the most promising approach or combine insights from multiple solutions.",
            contexts_list=refined_solutions
        )

        # Step 5: Final Verification
        final_solution = await self.revise(
            instruction="Verify the final solution for logical consistency, mathematical accuracy, and precision. "
                        "Ensure the answer format matches the expected output.",
            context=best_solution
        )

        return final_solution