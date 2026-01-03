# Workflow ID: drop_38_0
# Benchmark: drop
# Data Indices: [490, 125]

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

        # Step 1: Extract all entities and relationships from the passage
        entities = await self.generate(
            instruction="""Extract all named entities, numbers, dates, and relationships from the passage. 
            Format as a structured list with categories:
            - People: [names and roles]
            - Places: [locations and contexts]
            - Numbers: [values and what they represent]
            - Dates: [dates and their significance]
            - Actions: [what happens and when]""",
            context=""
        )

        # Step 2: Analyze the question to classify its type and resolve references
        question_analysis = await self.generate(
            instruction=f"""Analyze the question and classify its type (e.g., arithmetic, comparison, span extraction). 
            Resolve all references to entities using the extracted data:
            {entities}
            
            Output:
            - Question type
            - Resolved references
            - Required operations""",
            context=""
        )

        # Step 3: Perform operations based on the question type
        # Generate multiple interpretations for ambiguous questions
        interpretations = await asyncio.gather(
            self.generate(
                instruction=f"""Interpret the question as an arithmetic problem:
                {question_analysis}""",
                context=entities
            ),
            self.generate(
                instruction=f"""Interpret the question as a comparison problem:
                {question_analysis}""",
                context=entities
            ),
            self.generate(
                instruction=f"""Interpret the question as a span extraction problem:
                {question_analysis}""",
                context=entities
            )
        )

        # Combine interpretations using ensemble voting
        combined_interpretation = await self.ensemble(
            instruction="Select the most plausible interpretation and combine insights from all interpretations.",
            contexts_list=interpretations
        )

        # Step 4: Validate and format the answer
        final_answer = await self.generate(
            instruction=f"""Validate the answer against the expected format (e.g., number, date, text span).
            Ensure the answer is derived directly from the passage and matches exactly:
            {combined_interpretation}""",
            context=entities
        )

        return final_answer