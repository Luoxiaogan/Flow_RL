# Workflow ID: drop_24_0
# Benchmark: drop
# Data Indices: [304, 256]

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

        # Step 1: Extract entities, numbers, and relationships from the passage
        entities = await self.generate(
            instruction="""Extract all named entities, numbers, and relationships:
            - Entities: Names, places, organizations, etc.
            - Numbers: Values and what they represent
            - Relationships: Connections between entities and actions
            Format as a structured list.""",
            context=""
        )

        # Step 2: Classify the question type
        question_type = await self.generate(
            instruction=f"""Classify the question type based on the following:
            Passage: {self.problem_text}
            Entities: {entities}
            
            Possible types:
            - Arithmetic (addition, subtraction, etc.)
            - Counting (how many times, how many entities)
            - Comparison (greater than, less than, etc.)
            - Span Extraction (exact text span)
            
            Provide the classification and reasoning.""",
            context=entities
        )

        # Step 3: Map question references to passage entities
        reference_mapping = await self.generate(
            instruction=f"""Map references in the question to specific entities in the passage:
            Passage: {self.problem_text}
            Entities: {entities}
            Question: {self.problem_text.split('**QUESTION:**')[1].strip()}
            
            Resolve pronouns and partial names to specific entities.""",
            context=question_type
        )

        # Step 4: Execute operations based on question type
        if "arithmetic" in question_type.lower():
            # Extract numbers and perform calculations
            numbers = await self.generate(
                instruction=f"""Extract all relevant numbers from the passage:
                Passage: {self.problem_text}
                Entities: {entities}
                
                Perform the required arithmetic operation based on the question.""",
                context=reference_mapping
            )
            result = await self.generate(
                instruction=f"""Perform the arithmetic operation:
                Numbers: {numbers}
                Question: {self.problem_text.split('**QUESTION:**')[1].strip()}
                
                Show all steps and provide the final answer.""",
                context=numbers
            )
        elif "counting" in question_type.lower():
            # Count occurrences of specific entities or events
            count = await self.generate(
                instruction=f"""Count occurrences of the specified entity or event:
                Passage: {self.problem_text}
                Entities: {entities}
                Question: {self.problem_text.split('**QUESTION:**')[1].strip()}
                
                Provide the count and reasoning.""",
                context=reference_mapping
            )
            result = count
        elif "comparison" in question_type.lower():
            # Compare entities or values
            comparison = await self.generate(
                instruction=f"""Compare the specified entities or values:
                Passage: {self.problem_text}
                Entities: {entities}
                Question: {self.problem_text.split('**QUESTION:**')[1].strip()}
                
                Determine which is greater/longer/more and provide reasoning.""",
                context=reference_mapping
            )
            result = comparison
        elif "span extraction" in question_type.lower():
            # Extract exact text span
            span = await self.generate(
                instruction=f"""Extract the exact text span that answers the question:
                Passage: {self.problem_text}
                Entities: {entities}
                Question: {self.problem_text.split('**QUESTION:**')[1].strip()}
                
                Ensure the span matches the passage exactly.""",
                context=reference_mapping
            )
            result = span

        # Step 5: Format and validate the answer
        final_answer = await self.revise(
            instruction=f"""Format the answer appropriately and validate it:
            Passage: {self.problem_text}
            Entities: {entities}
            Question: {self.problem_text.split('**QUESTION:**')[1].strip()}
            Result: {result}
            
            Ensure the answer matches the expected format and is correct.""",
            context=result
        )

        return final_answer