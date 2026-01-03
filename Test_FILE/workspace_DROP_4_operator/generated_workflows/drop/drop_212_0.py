# Workflow ID: drop_212_0
# Benchmark: drop
# Data Indices: [470, 405]

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
        extraction = await self.generate(
            instruction="""Extract all named entities, numbers, and relationships:
            Format as structured list with categories:
            - People: [names and roles]
            - Places: [locations and contexts]
            - Numbers: [values and what they represent]
            - Actions: [what happens and when]""",
            context=""
        )

        # Step 2: Classify the question type
        classification = await self.generate(
            instruction=f"""Classify the question based on the following:
            Entities: {extraction}
            
            Identify the type of operation required:
            - Arithmetic (addition, subtraction, etc.)
            - Counting
            - Comparison
            - Span extraction
            Provide clear classification.""",
            context=extraction
        )

        # Step 3: Branch based on classification
        if "arithmetic" in classification.lower():
            # Extract relevant numbers and perform operation
            numbers = await self.generate(
                instruction=f"""Extract all relevant numbers from the passage:
                Entities: {extraction}
                
                Perform the required arithmetic operation (addition, subtraction, etc.) and provide the result.""",
                context=extraction
            )
            result = await self.revise(
                instruction="Validate the arithmetic result and ensure precision.",
                context=numbers
            )
        elif "counting" in classification.lower():
            # Count occurrences of specific entities
            count = await self.generate(
                instruction=f"""Count the occurrences of the specified entity:
                Entities: {extraction}
                
                Provide the exact count.""",
                context=extraction
            )
            result = await self.revise(
                instruction="Ensure the count is accurate and matches the passage.",
                context=count
            )
        elif "comparison" in classification.lower():
            # Compare two values or entities
            comparison = await self.generate(
                instruction=f"""Compare the specified values or entities:
                Entities: {extraction}
                
                Provide the result of the comparison.""",
                context=extraction
            )
            result = await self.revise(
                instruction="Validate the comparison result and ensure clarity.",
                context=comparison
            )
        elif "span extraction" in classification.lower():
            # Extract exact text span
            span = await self.generate(
                instruction=f"""Extract the exact text span that answers the question:
                Entities: {extraction}
                
                Ensure the span matches the passage exactly.""",
                context=extraction
            )
            result = await self.revise(
                instruction="Validate the extracted span and ensure exactness.",
                context=span
            )
        else:
            # Default comprehensive approach
            result = await self.generate(
                instruction=f"""Solve the problem using the extracted information:
                Entities: {extraction}
                
                Provide a complete and accurate answer.""",
                context=extraction
            )

        # Step 4: Synthesize and finalize the answer
        final_answer = await self.ensemble(
            instruction="Select the best answer from the provided options or synthesize a unified response.",
            contexts_list=[result]
        )

        return final_answer