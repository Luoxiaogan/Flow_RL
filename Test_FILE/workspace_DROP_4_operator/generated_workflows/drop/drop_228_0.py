# Workflow ID: drop_228_0
# Benchmark: drop
# Data Indices: [67, 415]

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

        # Step 1: Extract entities and classify question type (parallel)
        extract_instruction = """Extract all entities, numbers, and relationships from the passage:
        - Entities: [names, teams, locations]
        - Numbers: [values and what they represent]
        - Relationships: [actions, events, and their participants]"""
        classify_instruction = """Classify the question into one of the following types:
        - Arithmetic (addition, subtraction, etc.)
        - Counting (how many times, how many different, etc.)
        - Comparison (which is greater, longer, etc.)
        - Span Extraction (who did, what was the name of, etc.)
        - Multi-step (requires chaining multiple operations)"""

        extract_task = self.generate(extract_instruction, "")
        classify_task = self.generate(classify_instruction, "")
        entities, question_type = await asyncio.gather(extract_task, classify_task)

        # Step 2: Conditional branching based on question type
        if "arithmetic" in question_type.lower():
            result = await self.handle_arithmetic(entities)
        elif "counting" in question_type.lower():
            result = await self.handle_counting(entities)
        elif "comparison" in question_type.lower():
            result = await self.handle_comparison(entities)
        elif "span extraction" in question_type.lower():
            result = await self.handle_span_extraction(entities)
        elif "multi-step" in question_type.lower():
            result = await self.handle_multi_step(entities)
        else:
            result = "Unable to classify question type."

        # Step 3: Refine and validate the result
        refined_result = await self.revise(
            instruction="Validate and refine the result based on context.",
            context=result
        )

        return refined_result

    async def handle_arithmetic(self, context):
        instruction = f"""Perform arithmetic operations based on the extracted numbers:
        - Identify relevant numbers from: {context}
        - Determine the operation (addition, subtraction, etc.)
        - Compute the result."""
        return await self.generate(instruction, context)

    async def handle_counting(self, context):
        instruction = f"""Count instances of specific entities or events:
        - Identify target entities/events from: {context}
        - Tally occurrences accurately."""
        return await self.generate(instruction, context)

    async def handle_comparison(self, context):
        instruction = f"""Compare two or more values/entities:
        - Identify values/entities to compare from: {context}
        - Determine the comparison criteria (greater, longer, etc.)
        - Provide the result."""
        return await self.generate(instruction, context)

    async def handle_span_extraction(self, context):
        instruction = f"""Extract exact text spans matching the question:
        - Identify relevant spans from: {context}
        - Ensure the span matches the passage exactly."""
        return await self.generate(instruction, context)

    async def handle_multi_step(self, context):
        instruction = f"""Solve multi-step problems by chaining operations:
        - Identify required operations from: {context}
        - Execute operations in sequence."""
        return await self.generate(instruction, context)