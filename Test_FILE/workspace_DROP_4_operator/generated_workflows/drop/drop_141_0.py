# Workflow ID: drop_141_0
# Benchmark: drop
# Data Indices: [232, 18]

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

        # Step 1: Extract entities and numbers from the passage
        entities_and_numbers = await self.generate(
            instruction="""Extract all named entities, numbers, and relationships from the passage:
            - Entities: People, places, organizations
            - Numbers: Values and what they represent
            - Relationships: How entities and numbers are connected""",
            context=""
        )

        # Step 2: Resolve references in the question
        resolved_references = await self.generate(
            instruction=f"""Resolve references in the question by mapping them to passage entities:
            Passage Information: {entities_and_numbers}
            Question: [QUESTION]
            Map pronouns and partial names to specific entities.""",
            context=entities_and_numbers
        )

        # Step 3: Classify the problem type and identify required operations
        problem_classification = await self.generate(
            instruction=f"""Classify the problem type and identify required operations:
            Passage Information: {entities_and_numbers}
            Resolved References: {resolved_references}
            Question: [QUESTION]
            Possible types: Arithmetic, Counting, Comparison, Span Extraction
            Required operations: Addition, Subtraction, Counting, Comparison, Exact Extraction""",
            context=resolved_references
        )

        # Step 4: Execute operations based on problem type
        if "arithmetic" in problem_classification.lower():
            # Perform arithmetic operations in parallel
            operations = ["Addition", "Subtraction", "Multiplication", "Division"]
            results = await asyncio.gather(
                *[self.generate(instruction=f"Perform {op} operation based on passage information.", context=resolved_references) for op in operations]
            )
            final_result = await self.ensemble(
                instruction="Synthesize arithmetic results into final answer.",
                contexts_list=results
            )
        elif "counting" in problem_classification.lower():
            # Count instances in parallel
            entities_to_count = ["field goals", "interceptions", "turnovers"]
            counts = await asyncio.gather(
                *[self.generate(instruction=f"Count instances of {entity} in passage.", context=resolved_references) for entity in entities_to_count]
            )
            final_result = await self.ensemble(
                instruction="Synthesize counts into final answer.",
                contexts_list=counts
            )
        elif "comparison" in problem_classification.lower():
            # Compare values in parallel
            values_to_compare = ["field goal distances", "contract amounts", "years"]
            comparisons = await asyncio.gather(
                *[self.generate(instruction=f"Compare {value} in passage.", context=resolved_references) for value in values_to_compare]
            )
            final_result = await self.ensemble(
                instruction="Synthesize comparisons into final answer.",
                contexts_list=comparisons
            )
        elif "span extraction" in problem_classification.lower():
            # Extract text spans in parallel
            spans_to_extract = ["field goals", "team names", "dates"]
            extractions = await asyncio.gather(
                *[self.generate(instruction=f"Extract text span for {span} from passage.", context=resolved_references) for span in spans_to_extract]
            )
            final_result = await self.ensemble(
                instruction="Synthesize extracted spans into final answer.",
                contexts_list=extractions
            )
        else:
            # Default comprehensive approach
            final_result = await self.generate(
                instruction="Apply general problem-solving framework to derive final answer.",
                context=resolved_references
            )

        # Step 5: Validate and refine the result
        validated_result = await self.generate(
            instruction=f"""Validate the result to ensure it matches the expected format:
            Expected formats: Number, Date, Text Span
            Result: {final_result}""",
            context=final_result
        )
        refined_result = await self.revise(
            instruction="Refine the result to correct errors and improve clarity.",
            context=validated_result
        )

        return refined_result