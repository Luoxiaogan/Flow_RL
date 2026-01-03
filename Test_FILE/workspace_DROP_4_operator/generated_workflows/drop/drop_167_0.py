# Workflow ID: drop_167_0
# Benchmark: drop
# Data Indices: [322, 1]

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

        # Step 1: Extract key information
        entities = await self.generate(
            instruction="""Extract all named entities, numbers, and relationships:
            - Named entities (people, places, organizations)
            - Numbers and their contexts
            - Relationships between entities
            Format as a structured list.""",
            context=""
        )

        # Step 2: Analyze the question
        question_analysis = await self.generate(
            instruction="""Classify the question into one of the following categories:
            1. Arithmetic (addition, subtraction, etc.)
            2. Counting (how many times, how many different, etc.)
            3. Comparison (which is greater, who had more, etc.)
            4. Span extraction (who did, what was the name of, etc.)
            5. Multi-step reasoning (requires chaining multiple operations)
            Provide the category and reasoning.""",
            context=entities
        )

        # Step 3: Resolve references
        resolved_entities = await self.revise(
            instruction="""Resolve any pronouns or partial names to specific entities:
            - Identify all references (e.g., 'they', 'the team')
            - Map them to the correct entities from the extracted list""",
            context=entities
        )

        # Step 4: Perform operations
        operation_result = ""
        if "counting" in question_analysis.lower():
            operation_result = await self.generate(
                instruction=f"""Count the instances of the specified entity/event:
                Entities: {resolved_entities}
                Question: {question_analysis}""",
                context=resolved_entities
            )
        elif "arithmetic" in question_analysis.lower():
            operation_result = await self.generate(
                instruction=f"""Perform the required arithmetic operation:
                Extract relevant numbers from: {resolved_entities}
                Operation: {question_analysis}""",
                context=resolved_entities
            )
        elif "comparison" in question_analysis.lower():
            operation_result = await self.ensemble(
                instruction=f"""Compare the specified values/attributes:
                Entities: {resolved_entities}
                Question: {question_analysis}""",
                contexts_list=[resolved_entities, question_analysis]
            )
        elif "span extraction" in question_analysis.lower():
            operation_result = await self.generate(
                instruction=f"""Extract the exact text span that answers the question:
                Passage: {self.problem_text}
                Question: {question_analysis}""",
                context=resolved_entities
            )
        elif "multi-step" in question_analysis.lower():
            intermediate_results = await asyncio.gather(
                self.generate(
                    instruction=f"""First operation: {question_analysis.split('then')[0]}""",
                    context=resolved_entities
                ),
                self.generate(
                    instruction=f"""Second operation: {question_analysis.split('then')[1]}""",
                    context=resolved_entities
                )
            )
            operation_result = await self.ensemble(
                instruction="Combine results from both operations",
                contexts_list=intermediate_results
            )

        # Step 5: Format the answer
        final_answer = await self.revise(
            instruction=f"""Format the answer to match the expected output:
            Operation result: {operation_result}
            Ensure the answer is concise and adheres to the required format.""",
            context=operation_result
        )

        return final_answer