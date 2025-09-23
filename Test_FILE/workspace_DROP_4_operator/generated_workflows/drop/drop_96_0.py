# Workflow ID: drop_96_0
# Benchmark: drop
# Data Indices: [396, 22]

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

        # Step 1: Initial Analysis - Extract key entities, numbers, and relationships
        initial_analysis = await self.generate(
            instruction="""Extract all named entities, numbers, and relationships from the passage:
            - Entities: People, places, organizations, etc.
            - Numbers: Values and what they represent
            - Relationships: Actions, events, and connections between entities
            Format as a structured list.""",
            context=""
        )

        # Step 2: Question Classification - Identify the required operation(s)
        question_analysis = await self.generate(
            instruction=f"""Classify the question based on the following:
            - Is it numerical, logical, or textual?
            - Does it require counting, arithmetic, comparison, or span extraction?
            - What is the expected answer format?
            Passage context: {initial_analysis}""",
            context=""
        )

        # Step 3: Parallel Processing - Generate multiple solution attempts
        solutions = await asyncio.gather(
            self.generate(
                instruction=f"""Solve using direct extraction:
                - Extract exact text spans or numbers from the passage.
                Context: {initial_analysis}""",
                context=question_analysis
            ),
            self.generate(
                instruction=f"""Solve using arithmetic computation:
                - Perform addition, subtraction, or comparison as needed.
                Context: {initial_analysis}""",
                context=question_analysis
            ),
            self.generate(
                instruction=f"""Solve using multi-hop reasoning:
                - Combine multiple pieces of information from the passage.
                Context: {initial_analysis}""",
                context=question_analysis
            )
        )

        # Step 4: Validation and Synthesis - Validate each solution and synthesize the best answer
        validated_solutions = await asyncio.gather(
            *[self.revise(
                instruction=f"""Validate this solution:
                - Check for accuracy and adherence to the expected format.
                - Resolve any ambiguities or errors.
                Context: {solution}""",
                context=solution
            ) for solution in solutions]
        )
        best_solution = await self.ensemble(
            instruction="""Select the most accurate and complete solution:
            - Ensure the answer matches the expected format.
            - Prefer solutions with clear reasoning and validation.""",
            contexts_list=validated_solutions
        )

        # Step 5: Iterative Refinement - Refine the solution if necessary
        refined_solution = best_solution
        for _ in range(3):  # Allow up to 3 refinement iterations
            validation = await self.generate(
                instruction=f"""Validate the current solution:
                - Are there any errors or ambiguities?
                - Does it fully answer the question?
                Context: {refined_solution}""",
                context=refined_solution
            )
            if "error" in validation.lower() or "ambiguous" in validation.lower():
                refined_solution = await self.revise(
                    instruction=f"""Refine the solution based on validation feedback:
                    - Address errors or ambiguities.
                    - Improve clarity and completeness.
                    Context: {validation}""",
                    context=refined_solution
                )
            else:
                break

        return refined_solution