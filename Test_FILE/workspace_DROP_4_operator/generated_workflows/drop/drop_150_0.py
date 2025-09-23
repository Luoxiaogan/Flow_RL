# Workflow ID: drop_150_0
# Benchmark: drop
# Data Indices: [197, 452]

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

        # Step 1: Parallel Extraction of Entities, Relationships, and Numbers
        entities_task = self.generate(
            instruction="""Extract all named entities (people, teams, etc.) from the passage. 
            Format as a list of entities with their roles.""",
            context=""
        )
        relationships_task = self.generate(
            instruction="""Identify relationships between entities (e.g., who scored what). 
            Format as pairs of related entities.""",
            context=""
        )
        numbers_task = self.generate(
            instruction="""Extract all numbers and their associated contexts (e.g., scores, counts). 
            Format as a list of numbers with descriptions.""",
            context=""
        )

        entities, relationships, numbers = await asyncio.gather(entities_task, relationships_task, numbers_task)

        # Step 2: Question Decomposition
        question_analysis = await self.generate(
            instruction=f"""Analyze the question and identify:
            - What entities are involved?
            - What operation is required (e.g., count, compare, extract)?
            Passage Entities: {entities}
            Relationships: {relationships}
            Numbers: {numbers}""",
            context=""
        )

        # Step 3: Reference Resolution
        resolved_references = await self.revise(
            instruction=f"""Resolve any ambiguous references in the question using the passage. 
            Entities: {entities}
            Relationships: {relationships}""",
            context=question_analysis
        )

        # Step 4: Operation Execution (Conditional Branching)
        if "count" in question_analysis.lower():
            # Counting Task
            count_result = await self.generate(
                instruction=f"""Count the occurrences of the specified entity or event. 
                Entities: {entities}
                Relationships: {relationships}
                Numbers: {numbers}""",
                context=resolved_references
            )
            final_answer = count_result
        elif "compare" in question_analysis.lower():
            # Comparison Task
            comparison_result = await self.generate(
                instruction=f"""Compare the specified entities or values. 
                Entities: {entities}
                Relationships: {relationships}
                Numbers: {numbers}""",
                context=resolved_references
            )
            final_answer = comparison_result
        else:
            # Span Extraction Task
            span_extraction = await self.generate(
                instruction=f"""Extract the exact text span that answers the question. 
                Entities: {entities}
                Relationships: {relationships}""",
                context=resolved_references
            )
            final_answer = span_extraction

        # Step 5: Answer Validation and Formatting
        validated_answer = await self.revise(
            instruction="""Ensure the answer matches the expected format (number, date, text span). 
            Correct any discrepancies.""",
            context=final_answer
        )

        return validated_answer