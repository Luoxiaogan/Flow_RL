# Workflow ID: drop_69_0
# Benchmark: drop
# Data Indices: [219, 275]

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
            - Extract all named entities, numbers, and relationships.
            - Classify the question type (arithmetic, counting, comparison, span extraction).
            - Identify key constraints and conditions.
            Provide structured output.""",
            context=""
        )

        # Step 2: Parallel Exploration - Generate multiple solution strategies
        numerical_solution = self.generate(
            instruction=f"""Solve using numerical reasoning:
            - Perform arithmetic operations as needed.
            - Validate calculations.
            Context: {initial_analysis}""",
            context=initial_analysis
        )
        textual_solution = self.generate(
            instruction=f"""Solve using textual reasoning:
            - Extract relevant spans from the passage.
            - Resolve references and ambiguities.
            Context: {initial_analysis}""",
            context=initial_analysis
        )
        solutions = await asyncio.gather(numerical_solution, textual_solution)

        # Step 3: Conditional Branching - Select the best strategy
        selected_strategy = await self.ensemble(
            instruction="""Evaluate and select the best solution:
            - Numerical reasoning is preferred for arithmetic questions.
            - Textual reasoning is preferred for span extraction or reference resolution.
            Contexts: [Numerical Solution, Textual Solution]""",
            contexts_list=solutions
        )

        # Step 4: Iterative Refinement - Validate and refine the solution
        refined_solution = selected_strategy
        for _ in range(3):  # Allow up to 3 refinement iterations
            validation = await self.generate(
                instruction=f"""Validate the solution:
                - Check for unresolved references or ambiguities.
                - Ensure the format matches the expected output.
                Context: {refined_solution}""",
                context=refined_solution
            )
            if "error" in validation.lower():
                refined_solution = await self.revise(
                    instruction=f"""Revise the solution:
                    - Address issues identified during validation.
                    Context: {validation}""",
                    context=refined_solution
                )
            else:
                break

        # Step 5: Final Synthesis - Consolidate into a single answer
        final_answer = await self.summarize(
            instruction=f"""Summarize the final solution:
            - Ensure the answer is concise and matches the expected format.
            Context: {refined_solution}""",
            context=refined_solution
        )

        return final_answer