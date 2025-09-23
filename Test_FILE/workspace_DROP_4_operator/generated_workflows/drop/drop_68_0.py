# Workflow ID: drop_68_0
# Benchmark: drop
# Data Indices: [318, 69]

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
        entities = await self.generate(
            instruction="""Extract all named entities, numbers, and relationships from the passage:
            - Named entities: People, places, organizations
            - Numbers: Values and their contextual meanings
            - Relationships: Connections between entities""",
            context=""
        )

        # Step 2: Classify the question type
        question_type = await self.generate(
            instruction=f"""Classify the question based on the following categories:
            1. Arithmetic: Addition, subtraction, etc.
            2. Counting: Counting occurrences or items
            3. Comparison: Comparing values or attributes
            4. Span Extraction: Identifying exact text spans
            Passage entities and relationships:
            {entities}""",
            context=""
        )

        # Step 3: Resolve references
        resolved_references = await self.generate(
            instruction=f"""Resolve all pronouns and partial references in the question:
            Entities and relationships:
            {entities}
            Question:
            **QUESTION:**""",
            context=question_type
        )

        # Step 4: Execute operations
        operations = await asyncio.gather(
            self.generate(
                instruction=f"""Perform arithmetic operations if required:
                Context:
                {resolved_references}""",
                context=question_type
            ),
            self.generate(
                instruction=f"""Perform counting operations if required:
                Context:
                {resolved_references}""",
                context=question_type
            ),
            self.generate(
                instruction=f"""Perform comparison operations if required:
                Context:
                {resolved_references}""",
                context=question_type
            ),
            self.generate(
                instruction=f"""Extract exact text spans if required:
                Context:
                {resolved_references}""",
                context=question_type
            )
        )

        # Step 5: Validate and refine answers
        validated_answer = await self.ensemble(
            instruction="""Select the best answer based on:
            - Correctness: Matches the expected format
            - Completeness: Covers all aspects of the question
            - Clarity: Easy to understand and unambiguous""",
            contexts_list=operations
        )

        return validated_answer