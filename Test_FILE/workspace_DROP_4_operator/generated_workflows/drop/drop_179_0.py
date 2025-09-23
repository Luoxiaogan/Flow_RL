# Workflow ID: drop_179_0
# Benchmark: drop
# Data Indices: [319, 342]

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
            instruction="""Extract all named entities, numbers, and relationships from the passage:
            - Categorize entities (people, places, organizations, etc.)
            - Associate numbers with their context (e.g., years, counts, measurements)
            - Identify relationships between entities (e.g., 'Hungarians' → 'they')""",
            context=""
        )
        
        # Step 2: Resolve references and refine extraction
        refined = await self.revise(
            instruction="""Resolve pronouns and partial names to specific entities:
            - Ensure each reference points to the correct entity
            - Maintain coherence across sentences""",
            context=extraction
        )
        
        # Step 3: Classify problem type and identify required operation
        classification = await self.generate(
            instruction="""Classify the problem type based on the question:
            - Arithmetic (addition, subtraction, etc.)
            - Counting
            - Comparison
            - Span extraction
            Provide clear reasoning for the classification.""",
            context=refined
        )
        
        # Step 4: Execute the identified operation
        execution = await self.generate(
            instruction=f"""Based on the classification:
            Classification: {classification}
            
            Execute the required operation:
            - For arithmetic, perform calculations carefully
            - For counting, ensure all instances are included
            - For comparison, compare values accurately
            - For span extraction, match text exactly""",
            context=refined
        )
        
        # Step 5: Format the answer appropriately
        formatted_answer = await self.summarize(
            instruction="""Condense the result into the required format:
            - Number only
            - Exact text span
            - Date format if applicable""",
            context=execution
        )
        
        return formatted_answer