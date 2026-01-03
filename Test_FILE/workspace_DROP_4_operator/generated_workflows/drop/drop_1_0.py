# Workflow ID: drop_1_0
# Benchmark: drop
# Data Indices: [427, 139]

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
        import re

        # Step 1: Initial Analysis - Extract entities and classify question
        initial_analysis = await self.generate(
            instruction="""Extract all entities, numbers, and relationships from the passage.
            Resolve pronouns and partial names to their antecedents.
            Classify the question type (arithmetic, counting, comparison, span extraction).
            Identify the required operation(s).""",
            context=""
        )

        # Step 2: Parallel Processing - Generate multiple solution attempts
        solutions = await asyncio.gather(
            self.generate(
                instruction="Solve using arithmetic operations (addition, subtraction, etc.)",
                context=initial_analysis
            ),
            self.generate(
                instruction="Solve using counting (identify occurrences of specific events or entities)",
                context=initial_analysis
            ),
            self.generate(
                instruction="Solve using comparison (determine greater, lesser, or meeting criteria)",
                context=initial_analysis
            ),
            self.generate(
                instruction="Solve using span extraction (extract exact text spans)",
                context=initial_analysis
            )
        )

        # Step 3: Ensemble - Select the best solution
        best_solution = await self.ensemble(
            instruction="Select the most accurate and complete answer based on the question.",
            contexts_list=solutions
        )

        # Step 4: Iterative Refinement - Validate and refine the solution
        for _ in range(3):  # Maximum 3 iterations
            validation = await self.generate(
                instruction="Validate the solution against the question and passage.",
                context=best_solution
            )
            if "error" not in validation.lower():
                break
            best_solution = await self.revise(
                instruction=f"Refine the solution based on validation feedback: {validation}",
                context=best_solution
            )

        # Step 5: Final Output - Format the answer
        final_answer = await self.generate(
            instruction="Format the answer according to the expected output type (number, date, text span).",
            context=best_solution
        )

        return final_answer