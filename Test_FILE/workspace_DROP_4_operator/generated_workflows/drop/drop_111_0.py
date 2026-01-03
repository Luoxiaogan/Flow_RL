# Workflow ID: drop_111_0
# Benchmark: drop
# Data Indices: [352, 179]

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
        entities_task = self.generate(
            instruction="""Extract all named entities, relationships, and numerical data:
            - People: [names and roles]
            - Places: [locations and contexts]
            - Numbers: [values and what they represent]
            - Actions: [what happens and when]""",
            context=""
        )
        classification_task = self.generate(
            instruction="""Classify the problem type:
            - Is it arithmetic, counting, comparison, or span extraction?
            - What is the expected answer format?""",
            context=""
        )
        entities, classification = await asyncio.gather(entities_task, classification_task)

        # Step 2: Reference Resolution
        resolved_entities = await self.revise(
            instruction=f"""Resolve pronouns and partial names:
            - Map 'he', 'she', 'they', etc., to specific entities in the passage.
            - Ensure all references are clear and unambiguous.""",
            context=entities
        )

        # Step 3: Operation Identification and Execution
        if "arithmetic" in classification.lower():
            numbers = await self.generate(
                instruction=f"""Extract all relevant numbers from the passage:
                - Identify their context and relationships.
                - Determine the required operation (addition, subtraction, etc.).""",
                context=resolved_entities
            )
            result = await self.generate(
                instruction=f"""Perform the required arithmetic operation:
                - Show all steps clearly.
                - Present the final answer with appropriate units.""",
                context=numbers
            )
        elif "span extraction" in classification.lower():
            result = await self.generate(
                instruction=f"""Identify the exact text span that answers the question:
                - Ensure the span matches the passage exactly.
                - Provide the span as the final answer.""",
                context=resolved_entities
            )
        else:
            # Default approach for other problem types
            result = await self.generate(
                instruction=f"""Solve the problem using logical reasoning:
                - Combine facts from the passage.
                - Ensure the answer matches the expected format.""",
                context=resolved_entities
            )

        # Step 4: Validation and Final Answer
        validated_result = await self.revise(
            instruction=f"""Validate the answer:
            - Ensure it matches the expected format (number, date, or text span).
            - Cross-check with the passage for exactness.""",
            context=result
        )

        return validated_result