# Workflow ID: drop_207_0
# Benchmark: drop
# Data Indices: [182, 388]

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

        # Step 1: Extract entities and relationships
        entities_task = self.generate(
            instruction="""Extract all named entities, numbers, and relationships from the passage:
            - People: [names and roles]
            - Places: [locations and contexts]
            - Numbers: [values and what they represent]
            - Actions: [what happens and when]
            Format as a structured list.""",
            context=""
        )

        # Step 2: Resolve references in the question
        references_task = self.generate(
            instruction="""Map all pronouns and partial names in the question to specific entities in the passage:
            - Provide clear mappings for each reference
            - Prioritize the most likely candidate based on context""",
            context=""
        )

        # Run extraction and reference resolution in parallel
        entities, references = await asyncio.gather(entities_task, references_task)

        # Step 3: Identify required operations
        operation = await self.generate(
            instruction=f"""Based on the question and extracted information:
            Entities: {entities}
            References: {references}
            
            Identify the required operation(s):
            - Is it numerical (addition, subtraction, etc.)?
            - Does it involve counting or comparison?
            - What is the expected answer format?""",
            context=f"{entities}\n{references}"
        )

        # Step 4: Execute operations
        if "numerical" in operation.lower():
            # Extract numbers and perform arithmetic
            numbers_task = self.generate(
                instruction="Extract all relevant numbers from the passage and their context.",
                context=entities
            )
            calculation_task = self.generate(
                instruction=f"""Perform the required arithmetic operation:
                Operation: {operation}
                Numbers: {{await numbers_task}}""",
                context=operation
            )
            numbers, result = await asyncio.gather(numbers_task, calculation_task)
        else:
            # Handle non-numerical operations (e.g., span extraction)
            result = await self.generate(
                instruction=f"""Extract the exact text span from the passage that answers the question:
                Question: {{self.problem_text.split('QUESTION:')[1].split('ANSWER:')[0].strip()}}
                Passage: {{self.problem_text.split('PASSAGE:')[1].split('QUESTION:')[0].strip()}}""",
                context=entities
            )

        # Step 5: Format and validate the answer
        formatted_answer = await self.revise(
            instruction=f"""Ensure the answer matches the expected format:
            - If numerical, present as a number
            - If textual, match the exact span from the passage
            - Validate against the original question and passage""",
            context=result
        )

        return formatted_answer