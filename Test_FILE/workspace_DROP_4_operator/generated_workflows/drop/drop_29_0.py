# Workflow ID: drop_29_0
# Benchmark: drop
# Data Indices: [465, 272]

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

        # Step 1: Problem Analysis
        problem_analysis = await self.generate(
            instruction="""Classify the problem type:
            - Is it arithmetic, counting, comparison, or span extraction?
            - Does it require multi-step reasoning?
            - What is the expected answer format?""",
            context=""
        )

        # Step 2: Entity and Number Extraction
        entities_extraction = await self.generate(
            instruction=f"""Extract all named entities, numbers, and relationships:
            Format as structured list with categories:
            - People: [names and roles]
            - Places: [locations and contexts]
            - Numbers: [values and what they represent]
            - Actions: [what happens and when]
            
            Problem Analysis: {problem_analysis}""",
            context=""
        )

        # Step 3: Reference Resolution
        resolved_entities = await self.revise(
            instruction=f"""Resolve references such as pronouns and partial names:
            Ensure all entities are unambiguous and linked to their mentions in the passage.
            
            Extracted Entities: {entities_extraction}""",
            context=entities_extraction
        )

        # Step 4: Operation Identification and Execution
        if "arithmetic" in problem_analysis.lower():
            operations = await self.generate(
                instruction=f"""Identify and perform arithmetic operations:
                - Extract relevant numbers
                - Apply addition, subtraction, etc.
                
                Resolved Entities: {resolved_entities}""",
                context=resolved_entities
            )
        elif "counting" in problem_analysis.lower():
            operations = await self.generate(
                instruction=f"""Count occurrences of specific entities or events:
                
                Resolved Entities: {resolved_entities}""",
                context=resolved_entities
            )
        elif "comparison" in problem_analysis.lower():
            operations = await self.generate(
                instruction=f"""Compare values or spans:
                
                Resolved Entities: {resolved_entities}""",
                context=resolved_entities
            )
        else:  # Span extraction
            operations = await self.generate(
                instruction=f"""Extract exact text spans matching the query:
                
                Resolved Entities: {resolved_entities}""",
                context=resolved_entities
            )

        # Step 5: Answer Formatting and Validation
        candidate_answers = await asyncio.gather(
            self.generate(instruction="Format answer as number", context=operations),
            self.generate(instruction="Format answer as text span", context=operations),
            self.generate(instruction="Format answer as date", context=operations)
        )
        final_answer = await self.ensemble(
            instruction="Select the most plausible answer based on problem requirements",
            contexts_list=candidate_answers
        )

        return final_answer