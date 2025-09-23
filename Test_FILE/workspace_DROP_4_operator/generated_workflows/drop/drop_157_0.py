# Workflow ID: drop_157_0
# Benchmark: drop
# Data Indices: [474, 463]

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

        # Step 1: Classify the problem type
        classification = await self.generate(
            instruction="""Classify the problem into one of the following categories:
            - Arithmetic: Involves addition, subtraction, multiplication, division.
            - Counting: Requires counting occurrences of entities or events.
            - Comparison: Asks for greater/lesser values or rankings.
            - Span Extraction: Seeks exact text spans from the passage.
            - Multi-step: Combines multiple operations or facts.
            Provide a clear category and justification.""",
            context=""
        )

        # Step 2: Extract relevant information from the passage
        extraction = await self.generate(
            instruction=f"""Extract all relevant entities, numbers, and relationships from the passage:
            - Entities: Named entities (teams, players, locations).
            - Numbers: Numerical values and their contexts.
            - Relationships: Actions and their participants.
            Focus on information related to the problem type: {classification}.""",
            context=classification
        )

        # Step 3: Resolve references
        resolved_references = await self.revise(
            instruction="Resolve pronouns and partial names to their corresponding entities in the passage.",
            context=extraction
        )

        # Step 4: Execute the required operation(s)
        if "Arithmetic" in classification:
            result = await self.generate(
                instruction=f"""Perform the required arithmetic operation using the extracted numbers:
                - Show all calculation steps.
                - Maintain full precision.
                - Present the final answer with appropriate units.
                Relevant information: {resolved_references}.""",
                context=resolved_references
            )
        elif "Counting" in classification:
            result = await self.generate(
                instruction=f"""Count the occurrences of the specified entities or events:
                - Clearly state what is being counted.
                - Provide the total count.
                Relevant information: {resolved_references}.""",
                context=resolved_references
            )
        elif "Comparison" in classification:
            result = await self.generate(
                instruction=f"""Compare the specified values or attributes:
                - State the comparison criteria.
                - Provide the result of the comparison.
                Relevant information: {resolved_references}.""",
                context=resolved_references
            )
        elif "Span Extraction" in classification:
            result = await self.generate(
                instruction=f"""Extract the exact text span matching the question:
                - Ensure the span matches the passage exactly.
                Relevant information: {resolved_references}.""",
                context=resolved_references
            )
        elif "Multi-step" in classification:
            intermediate_results = await asyncio.gather(
                self.generate(instruction="Solve the first part of the problem.", context=resolved_references),
                self.generate(instruction="Solve the second part of the problem.", context=resolved_references)
            )
            result = await self.ensemble(
                instruction="Combine intermediate results into a coherent final answer.",
                contexts_list=intermediate_results
            )
        else:
            result = await self.generate(
                instruction="Apply a general problem-solving framework to derive the answer.",
                context=resolved_references
            )

        # Step 5: Validate and refine the result
        refined_result = await self.revise(
            instruction="Validate the result against the expected format and refine if necessary.",
            context=result
        )

        return refined_result