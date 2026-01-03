# Workflow ID: drop_211_0
# Benchmark: drop
# Data Indices: [349, 340]

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

        # Step 1: Extract entities and numbers
        entities_extraction = await self.generate(
            instruction="""Extract all named entities, numbers, and relationships:
            Format as structured list with categories:
            - People: [names and roles]
            - Places: [locations and contexts]
            - Numbers: [values and what they represent]
            - Actions: [what happens and when]""",
            context=""
        )

        # Step 2: Resolve references in the question
        reference_resolution = await self.generate(
            instruction=f"""Resolve all pronouns and partial names in the question to specific entities:
            Entities extracted: {entities_extraction}
            Provide clear mappings.""",
            context=entities_extraction
        )

        # Step 3: Classify the question type
        question_classification = await self.generate(
            instruction=f"""Classify the question type based on the following:
            Entities: {entities_extraction}
            Resolved references: {reference_resolution}
            Determine if the question requires:
            - Arithmetic operations (addition, subtraction, etc.)
            - Counting
            - Comparison
            - Span extraction
            - Multi-step reasoning""",
            context=f"{entities_extraction}\n{reference_resolution}"
        )

        # Step 4: Execute required operations in parallel
        if "arithmetic" in question_classification.lower():
            arithmetic_operations = await asyncio.gather(
                self.generate(instruction="Perform addition where required", context=question_classification),
                self.generate(instruction="Perform subtraction where required", context=question_classification)
            )
            operation_results = await self.ensemble(
                instruction="Combine results of arithmetic operations",
                contexts_list=arithmetic_operations
            )
        elif "counting" in question_classification.lower():
            count_operations = await self.generate(
                instruction="Count instances as required by the question",
                context=question_classification
            )
            operation_results = count_operations
        elif "comparison" in question_classification.lower():
            comparison_operations = await self.generate(
                instruction="Compare values as required by the question",
                context=question_classification
            )
            operation_results = comparison_operations
        else:
            operation_results = await self.generate(
                instruction="Extract the required text span",
                context=question_classification
            )

        # Step 5: Validate and refine the final answer
        final_answer = await self.revise(
            instruction=f"""Validate and refine the answer:
            Operation results: {operation_results}
            Ensure the answer matches the expected format and is consistent with the passage.""",
            context=operation_results
        )

        return final_answer