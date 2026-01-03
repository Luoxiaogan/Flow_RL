# Workflow ID: drop_32_0
# Benchmark: drop
# Data Indices: [328, 267]

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

        # Step 1: Initial Analysis - Extract entities, relationships, and question type
        initial_analysis = await self.generate(
            instruction="""Analyze the problem structure:
            - Identify key entities (people, teams, events, etc.)
            - Extract all numbers and their contexts
            - Classify the question type (arithmetic, counting, comparison, span extraction)
            - Resolve pronouns and partial references to specific entities
            Provide a structured summary.""",
            context=""
        )

        # Step 2: Parallel Fork - Generate candidate solutions
        arithmetic_solution = self.generate(
            instruction=f"""Solve using arithmetic operations:
            - Extract relevant numbers from the passage
            - Perform addition, subtraction, or other required operations
            - Ensure calculations are precise
            Context: {initial_analysis}""",
            context=initial_analysis
        )
        counting_solution = self.generate(
            instruction=f"""Solve using counting:
            - Identify instances of the target entity or event
            - Count occurrences accurately
            - Ensure no instances are missed
            Context: {initial_analysis}""",
            context=initial_analysis
        )
        span_extraction_solution = self.generate(
            instruction=f"""Solve using span extraction:
            - Identify the exact text span answering the question
            - Ensure the span matches the passage exactly
            Context: {initial_analysis}""",
            context=initial_analysis
        )
        candidate_solutions = await asyncio.gather(arithmetic_solution, counting_solution, span_extraction_solution)

        # Step 3: Validation and Refinement - Iteratively improve solutions
        refined_solutions = []
        for solution in candidate_solutions:
            validated = await self.generate(
                instruction=f"""Validate the solution:
                - Check numerical correctness for arithmetic
                - Verify completeness for counting
                - Confirm exact match for span extraction
                Solution: {solution}""",
                context=solution
            )
            if "error" in validated.lower():
                refined = await self.revise(
                    instruction=f"""Refine the solution:
                    - Correct identified issues
                    - Re-validate the refined solution
                    Context: {validated}""",
                    context=solution
                )
                refined_solutions.append(refined)
            else:
                refined_solutions.append(validated)

        # Step 4: Ensemble Selection - Choose the best solution
        final_solution = await self.ensemble(
            instruction="""Select the best solution:
            - Prioritize numerical correctness for arithmetic
            - Ensure completeness for counting
            - Match exact text spans for extraction
            Evaluate all candidates and choose the most valid one.""",
            contexts_list=refined_solutions
        )

        return final_solution