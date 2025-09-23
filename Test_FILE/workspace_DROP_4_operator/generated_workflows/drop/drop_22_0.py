# Workflow ID: drop_22_0
# Benchmark: drop
# Data Indices: [34, 224]

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

        # Step 1: Extract entities, numbers, and relationships
        entity_extraction = await self.generate(
            instruction="""Extract all named entities, numbers, and relationships from the passage:
            - Identify people, places, teams, and other entities
            - Extract all numerical values and their contexts
            - Map pronouns and partial names to specific entities
            - Highlight relationships between entities (e.g., who did what, when, and where)
            Format as a structured list.""",
            context=""
        )

        # Step 2: Analyze the question type and required operations
        question_analysis = await self.generate(
            instruction=f"""Analyze the question and determine the required operations:
            - Is it a numerical question requiring arithmetic (addition, subtraction, etc.)?
            - Does it involve counting or comparison?
            - Is it a span extraction task requiring exact matching?
            - Identify all relevant entities and numbers from the passage that pertain to the question.
            Passage entities: {entity_extraction}
            Question: [QUESTION]""",
            context=entity_extraction
        )

        # Step 3: Generate multiple candidate solutions in parallel
        candidates = await asyncio.gather(
            self.generate(
                instruction=f"""Solve the problem assuming it requires arithmetic operations:
                - Extract relevant numbers from the passage
                - Perform addition, subtraction, or other required operations
                - Format the answer as a number or date.
                Passage entities: {entity_extraction}
                Question analysis: {question_analysis}""",
                context=entity_extraction
            ),
            self.generate(
                instruction=f"""Solve the problem assuming it requires span extraction:
                - Identify the exact text span in the passage that answers the question
                - Ensure the span matches the passage exactly.
                Passage entities: {entity_extraction}
                Question analysis: {question_analysis}""",
                context=entity_extraction
            ),
            self.generate(
                instruction=f"""Solve the problem assuming it requires comparison or ranking:
                - Compare entities, numbers, or events based on the question
                - Determine which is greater, longer, earlier, etc.
                Passage entities: {entity_extraction}
                Question analysis: {question_analysis}""",
                context=entity_extraction
            )
        )

        # Step 4: Ensemble selection to choose the best candidate
        final_answer = await self.ensemble(
            instruction="""Evaluate the candidate solutions and select the best one:
            - Check for accuracy and alignment with the question
            - Validate against the passage for exact matching
            - Choose the most plausible and well-supported answer.""",
            contexts_list=candidates
        )

        # Step 5: Refine the final answer for clarity and correctness
        refined_answer = await self.revise(
            instruction="""Refine the final answer:
            - Ensure it matches the expected format (number, date, or exact text span)
            - Double-check calculations and references
            - Improve clarity and remove ambiguity.""",
            context=final_answer
        )

        return refined_answer