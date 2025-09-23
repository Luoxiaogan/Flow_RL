# Workflow ID: drop_14_0
# Benchmark: drop
# Data Indices: [456, 326]

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

        # Step 1: Parallel Extraction of Entities and Numbers
        extraction_attempts = await asyncio.gather(
            self.generate(instruction="Extract all named entities, numbers, and relationships from the passage. Focus on people, places, numerical values, and their roles.", context=""),
            self.generate(instruction="Identify all actions, events, and temporal relationships in the passage. Pay attention to sequences and dependencies.", context="")
        )
        synthesized_context = await self.ensemble(
            instruction="Combine these extractions into a unified representation. Resolve overlaps and ensure completeness.",
            contexts_list=extraction_attempts
        )

        # Step 2: Reference Resolution
        resolved_references = await self.generate(
            instruction=f"""
            Resolve all pronouns and partial references in the question to specific entities in the passage.
            Passage Context: {synthesized_context}
            Question: Analyze the question and map references to entities.
            """,
            context=synthesized_context
        )

        # Step 3: Problem Classification
        problem_type = await self.generate(
            instruction=f"""
            Classify the problem type based on the question:
            1. Is it numerical, logical, or textual?
            2. Does it require addition, subtraction, counting, comparison, or span extraction?
            Synthesized Context: {synthesized_context}
            Resolved References: {resolved_references}
            """,
            context=resolved_references
        )

        # Step 4: Operation Execution with Validation
        if "addition" in problem_type.lower():
            result = await self.generate(
                instruction=f"""
                Perform addition based on the identified numbers and relationships.
                Context: {synthesized_context}
                Resolved References: {resolved_references}
                """,
                context=problem_type
            )
        elif "subtraction" in problem_type.lower():
            result = await self.generate(
                instruction=f"""
                Perform subtraction based on the identified numbers and relationships.
                Context: {synthesized_context}
                Resolved References: {resolved_references}
                """,
                context=problem_type
            )
        elif "counting" in problem_type.lower():
            result = await self.generate(
                instruction=f"""
                Count the relevant instances based on the identified entities and relationships.
                Context: {synthesized_context}
                Resolved References: {resolved_references}
                """,
                context=problem_type
            )
        else:
            result = await self.generate(
                instruction=f"""
                Extract the exact text span that answers the question.
                Context: {synthesized_context}
                Resolved References: {resolved_references}
                """,
                context=problem_type
            )

        # Step 5: Answer Formatting
        formatted_answer = await self.summarize(
            instruction=f"""
            Ensure the answer matches the expected format: numbers, dates, or exact text spans.
            Result: {result}
            """,
            context=result
        )

        return formatted_answer