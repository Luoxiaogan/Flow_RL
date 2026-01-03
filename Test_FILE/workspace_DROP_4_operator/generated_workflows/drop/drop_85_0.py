# Workflow ID: drop_85_0
# Benchmark: drop
# Data Indices: [414, 373]

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

        # Step 1: Extract all relevant entities, numbers, and relationships
        entities = await self.generate(
            instruction="""Extract all named entities, numbers, and relationships from the passage:
            - People: [names and roles]
            - Places: [locations and contexts]
            - Numbers: [values and what they represent]
            - Actions: [what happens and when]
            Format as a structured list.""",
            context=""
        )

        # Step 2: Resolve question references to specific entities
        resolved_references = await self.generate(
            instruction=f"""Resolve all pronouns and partial names in the question to specific entities:
            Passage Entities: {entities}
            Question: [question text]
            Provide a mapping of references to entities.""",
            context=entities
        )

        # Step 3: Identify the required operation(s)
        operation = await self.generate(
            instruction=f"""Classify the question and identify the required operation(s):
            Passage Entities: {entities}
            Resolved References: {resolved_references}
            Question: [question text]
            Categories: Arithmetic, Counting, Comparison, Span Extraction, Multi-step
            Provide the category and specific operation.""",
            context=f"{entities}

{resolved_references}"
        )

        # Step 4: Execute the identified operation(s)
        if "arithmetic" in operation.lower():
            # Perform arithmetic operations
            result = await self.generate(
                instruction=f"""Perform the required arithmetic operation:
                Passage Entities: {entities}
                Resolved References: {resolved_references}
                Operation: {operation}
                Show all steps and present the final answer.""",
                context=f"{entities}

{resolved_references}"
            )
        elif "counting" in operation.lower():
            # Perform counting operations
            result = await self.generate(
                instruction=f"""Count the required entities or occurrences:
                Passage Entities: {entities}
                Resolved References: {resolved_references}
                Operation: {operation}
                Present the count.""",
                context=f"{entities}

{resolved_references}"
            )
        elif "comparison" in operation.lower():
            # Perform comparison operations
            result = await self.generate(
                instruction=f"""Compare the specified values or spans:
                Passage Entities: {entities}
                Resolved References: {resolved_references}
                Operation: {operation}
                Present the comparison result.""",
                context=f"{entities}

{resolved_references}"
            )
        elif "span extraction" in operation.lower():
            # Perform span extraction
            result = await self.generate(
                instruction=f"""Extract the exact text span:
                Passage Entities: {entities}
                Resolved References: {resolved_references}
                Operation: {operation}
                Ensure the span matches the passage exactly.""",
                context=f"{entities}

{resolved_references}"
            )
        else:
            # Handle multi-step operations
            steps = await self.generate(
                instruction=f"""Break down the multi-step operation into individual steps:
                Passage Entities: {entities}
                Resolved References: {resolved_references}
                Operation: {operation}
                Execute each step and present the final result.""",
                context=f"{entities}

{resolved_references}"
            )
            result = await self.generate(
                instruction=f"""Execute the multi-step operation:
                Steps: {steps}
                Present the final result.""",
                context=f"{entities}

{resolved_references}"
            )

        # Step 5: Format the answer
        formatted_answer = await self.generate(
            instruction=f"""Format the answer to match the expected output:
            Result: {result}
            Ensure numbers are formatted correctly, dates are in the correct format, and text spans match exactly.""",
            context=result
        )

        return formatted_answer