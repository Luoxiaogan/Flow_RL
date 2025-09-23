# Workflow ID: drop_135_0
# Benchmark: drop
# Data Indices: [395, 120]

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
        entities_extraction = await self.generate(
            instruction="""Extract all named entities, numbers, and relationships from the passage. 
            Format as a structured list with categories:
            - People: [names and roles]
            - Places: [locations and contexts]
            - Numbers: [values and what they represent]
            - Actions: [what happens and when]""",
            context=""
        )

        # Step 2: Resolve references in the question
        reference_resolution = await self.generate(
            instruction=f"""Resolve all pronouns and partial references in the question to specific entities in the passage. 
            Passage entities: {entities_extraction}""",
            context=""
        )

        # Step 3: Classify the problem type
        problem_classification = await self.generate(
            instruction="""Classify the problem type based on the question. 
            Possible types include:
            - Arithmetic (addition, subtraction, percentage calculation)
            - Counting (how many times, how many different)
            - Comparison (greater than, less than, earlier, later)
            - Span Extraction (exact text span)""",
            context=reference_resolution
        )

        # Step 4: Execute solution based on problem type
        if "arithmetic" in problem_classification.lower():
            solution = await self.generate(
                instruction=f"""Perform the required arithmetic operation based on the question and passage. 
                Extracted entities: {entities_extraction}
                Resolved references: {reference_resolution}""",
                context=""
            )
        elif "counting" in problem_classification.lower():
            solution = await self.generate(
                instruction=f"""Count the relevant instances based on the question and passage. 
                Extracted entities: {entities_extraction}
                Resolved references: {reference_resolution}""",
                context=""
            )
        elif "comparison" in problem_classification.lower():
            solution = await self.generate(
                instruction=f"""Compare the relevant entities or values based on the question and passage. 
                Extracted entities: {entities_extraction}
                Resolved references: {reference_resolution}""",
                context=""
            )
        elif "span extraction" in problem_classification.lower():
            solution = await self.generate(
                instruction=f"""Extract the exact text span from the passage that answers the question. 
                Passage: {self.problem_text.split('**PASSAGE:**')[1].split('**QUESTION:**')[0].strip()}
                Resolved references: {reference_resolution}""",
                context=""
            )
        else:
            solution = await self.generate(
                instruction="Apply general problem-solving framework based on the question and passage.",
                context=""
            )

        # Step 5: Validate and refine the solution
        validated_solution = await self.revise(
            instruction="Ensure the solution matches the expected format and is logically consistent.",
            context=solution
        )

        return validated_solution