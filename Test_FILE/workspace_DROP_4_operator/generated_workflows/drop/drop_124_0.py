# Workflow ID: drop_124_0
# Benchmark: drop
# Data Indices: [45, 348]

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
            instruction="""Extract all named entities, numbers, and relationships from the passage.
            Format as a structured list:
            - People: [names and roles]
            - Places: [locations and contexts]
            - Numbers: [values and what they represent]
            - Actions: [what happens and when]""",
            context=""
        )

        # Step 2: Resolve references (pronouns, partial names)
        resolved_references = await self.generate(
            instruction=f"""Resolve all references in the passage:
            - Map pronouns to specific entities
            - Clarify partial names
            Passage entities: {entities}""",
            context=entities
        )

        # Step 3: Classify the question type
        question_type = await self.generate(
            instruction=f"""Classify the question type based on its phrasing:
            - Arithmetic: Addition, subtraction, etc.
            - Counting: How many times, how many different, etc.
            - Comparison: Which is greater, longer, etc.
            - Span Extraction: Who did, What was the name of, etc.
            - Multi-step: Requires chaining multiple operations
            Passage entities: {entities}
            Resolved references: {resolved_references}""",
            context=""
        )

        # Step 4: Execute operations based on classification
        if "arithmetic" in question_type.lower():
            numbers = await self.generate(
                instruction=f"""Extract all relevant numbers from the passage for arithmetic operations.
                Passage entities: {entities}""",
                context=resolved_references
            )
            result = await self.generate(
                instruction=f"""Perform the required arithmetic operation:
                - Addition: Sum the numbers
                - Subtraction: Subtract the smaller from the larger
                Relevant numbers: {numbers}""",
                context=numbers
            )
        elif "counting" in question_type.lower():
            count_result = await self.generate(
                instruction=f"""Count the occurrences of the specified entity or event in the passage.
                Passage entities: {entities}""",
                context=resolved_references
            )
            result = count_result
        elif "comparison" in question_type.lower():
            comparison_result = await self.generate(
                instruction=f"""Compare the specified entities or events in the passage.
                Passage entities: {entities}""",
                context=resolved_references
            )
            result = comparison_result
        elif "span extraction" in question_type.lower():
            span_result = await self.generate(
                instruction=f"""Extract the exact text span from the passage that answers the question.
                Passage entities: {entities}""",
                context=resolved_references
            )
            result = span_result
        else:
            # Default to multi-step reasoning
            steps = await self.generate(
                instruction=f"""Break the problem into smaller steps and solve each step sequentially.
                Passage entities: {entities}
                Resolved references: {resolved_references}""",
                context=question_type
            )
            result = steps

        # Step 5: Synthesize the final answer
        final_answer = await self.ensemble(
            instruction="Synthesize the final answer from the results of previous steps.",
            contexts_list=[entities, resolved_references, question_type, result]
        )

        # Step 6: Validate and refine the answer (optional)
        validated_answer = await self.revise(
            instruction=f"""Validate the answer against the passage and refine if necessary.
            Final answer: {final_answer}""",
            context=final_answer
        )

        return validated_answer