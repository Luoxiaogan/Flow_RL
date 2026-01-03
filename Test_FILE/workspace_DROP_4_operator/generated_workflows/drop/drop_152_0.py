# Workflow ID: drop_152_0
# Benchmark: drop
# Data Indices: [226, 441]

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
            instruction="""Extract all named entities, numbers, and relationships:
            - People: [names and roles]
            - Places: [locations and contexts]
            - Numbers: [values and what they represent]
            - Actions: [what happens and when]
            Format as structured list.""",
            context=""
        )

        # Step 2: Classify question type and identify required operations
        classification = await self.generate(
            instruction=f"""Classify the question type and identify required operations:
            Entities and context: {entities}
            - Is it numerical, logical, or textual?
            - Does it involve addition, subtraction, counting, comparison, or span extraction?
            Provide structured classification.""",
            context=entities
        )

        # Step 3: Branch based on question type
        if "numerical" in classification.lower() and "comparison" in classification.lower():
            # Parallel fact extraction for comparison questions
            fact1 = await self.generate(
                instruction=f"""Extract the first value for comparison:
                Context: {entities}""",
                context=entities
            )
            fact2 = await self.generate(
                instruction=f"""Extract the second value for comparison:
                Context: {entities}""",
                context=entities
            )
            # Ensemble to compute the result
            result = await self.ensemble(
                instruction="Perform the required operation (e.g., subtraction) and compute the result.",
                contexts_list=[fact1, fact2]
            )
        elif "counting" in classification.lower():
            # Count occurrences of a specific entity or event
            count = await self.generate(
                instruction=f"""Count the number of occurrences:
                Context: {entities}""",
                context=entities
            )
            result = count
        elif "span extraction" in classification.lower():
            # Extract exact text span
            result = await self.generate(
                instruction=f"""Extract the exact text span that answers the question:
                Context: {entities}""",
                context=entities
            )
        else:
            # Default approach for other question types
            result = await self.generate(
                instruction=f"""Solve the problem using general reasoning:
                Context: {entities}""",
                context=entities
            )

        # Step 4: Validate and refine the result
        validation = await self.revise(
            instruction=f"""Validate the result:
            - Check for correctness and consistency
            - Ensure the format matches the expected answer type
            Original result: {result}""",
            context=result
        )
        refined_result = validation if "error" not in validation.lower() else result

        # Step 5: Format the final answer
        final_answer = await self.summarize(
            instruction="Condense the final result into the required format (number, date, or text span).",
            context=refined_result
        )

        return final_answer