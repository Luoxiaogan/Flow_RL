# Workflow ID: drop_151_0
# Benchmark: drop
# Data Indices: [428, 15]

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

        # Step 1: Initial Analysis - Extract entities and classify question type
        entities_extraction, question_classification = await asyncio.gather(
            self.generate(
                instruction="""Extract all named entities, numbers, and relationships from the passage:
                - Entities: People, places, organizations
                - Numbers: Values and what they represent
                - Relationships: Connections between entities and numbers""",
                context=""
            ),
            self.generate(
                instruction="""Classify the question type:
                - Arithmetic: Addition, subtraction, comparison
                - Counting: How many times, how many different
                - Comparison: Which is greater, which came first
                - Span Extraction: Who did, what was the name of""",
                context=""
            )
        )

        # Step 2: Reference Resolution - Map ambiguous references to entities
        resolved_references = await self.generate(
            instruction=f"""Resolve ambiguous references in the question to specific entities in the passage:
            Passage Entities: {entities_extraction}
            Question: [Original Problem]
            Resolve pronouns and partial names to their corresponding entities.""",
            context=entities_extraction
        )

        # Step 3: Operation Execution - Perform the identified operation
        operation_result = await self.generate(
            instruction=f"""Based on the question classification:
            Classification: {question_classification}
            Resolved References: {resolved_references}
            
            Execute the required operation(s) using the extracted information:
            - Arithmetic: Perform calculations
            - Counting: Count instances
            - Comparison: Compare values
            - Span Extraction: Extract exact text spans""",
            context=f"{entities_extraction}

{resolved_references}"
        )

        # Step 4: Validation and Refinement - Ensure correctness
        validated_result = await self.revise(
            instruction=f"""Validate the operation result:
            - Check for missing instances
            - Ensure numerical operations account for units
            - Verify span extraction matches the passage exactly
            
            If errors are found, correct them.""",
            context=operation_result
        )

        # Step 5: Final Answer Synthesis - Format the result
        final_answer = await self.ensemble(
            instruction=f"""Synthesize the final answer:
            Validated Result: {validated_result}
            
            Format the answer according to the expected type:
            - Number only
            - Date format
            - Exact text span""",
            contexts_list=[validated_result, entities_extraction, resolved_references]
        )

        return final_answer