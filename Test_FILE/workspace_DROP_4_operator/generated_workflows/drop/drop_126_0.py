# Workflow ID: drop_126_0
# Benchmark: drop
# Data Indices: [298, 196]

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
            Format as a structured list.""",
            context=""
        )

        # Step 2: Analyze the question to determine required operations
        question_analysis = await self.generate(
            instruction=f"""Analyze the question and classify its type:
            - Is it arithmetic, counting, comparison, or span extraction?
            - Identify key phrases indicating the required operation(s).
            Entities for reference: {entities}""",
            context=entities
        )

        # Step 3: Perform parallel operations based on question type
        if "arithmetic" in question_analysis.lower():
            operations = await asyncio.gather(
                self.generate(instruction="Perform addition where applicable.", context=entities),
                self.generate(instruction="Perform subtraction where applicable.", context=entities)
            )
        elif "counting" in question_analysis.lower():
            operations = await asyncio.gather(
                self.generate(instruction="Count occurrences of each entity.", context=entities)
            )
        elif "comparison" in question_analysis.lower():
            operations = await asyncio.gather(
                self.generate(instruction="Compare magnitudes of relevant numbers.", context=entities)
            )
        else:  # Span extraction
            operations = await asyncio.gather(
                self.generate(instruction="Extract exact text spans matching the question.", context=entities)
            )

        # Step 4: Synthesize results using ensemble
        synthesized_answer = await self.ensemble(
            instruction="Synthesize results into a single coherent answer. Ensure it matches the expected format.",
            contexts_list=operations
        )

        # Step 5: Validate and refine the answer
        validated_answer = await self.revise(
            instruction="Validate the answer against the passage. Ensure exact matches for text spans and precision for numbers.",
            context=synthesized_answer
        )

        return validated_answer