# Workflow ID: drop_13_0
# Benchmark: drop
# Data Indices: [171, 260]

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
            instruction="""Analyze the question and classify it into one of the following categories:
            - Arithmetic: Involves numerical operations like addition, subtraction, etc.
            - Counting: Requires counting specific entities or events.
            - Comparison: Demands evaluating relationships between entities or values.
            - Span Extraction: Focuses on extracting exact text spans from the passage.
            - Multi-step: Combines multiple operations or requires chaining facts.
            
            Provide reasoning for your classification.""",
            context=""
        )

        # Step 2: Entity Extraction (Parallel with Reference Resolution)
        entity_extraction_task = self.generate(
            instruction="""Extract all relevant entities, numbers, and relationships from the passage:
            - Named entities (people, places, organizations)
            - Numerical values and their context
            - Relationships between entities""",
            context=""
        )
        reference_resolution_task = self.generate(
            instruction="""Resolve pronouns and partial names to specific entities in the passage:
            - Map 'he', 'she', 'they' to specific people
            - Map 'the team', 'the company' to specific organizations""",
            context=""
        )
        entities, resolved_references = await asyncio.gather(entity_extraction_task, reference_resolution_task)

        # Step 3: Operation Identification
        operation_identification = await self.generate(
            instruction=f"""Based on the problem analysis and extracted entities:
            Problem Analysis: {problem_analysis}
            Entities: {entities}
            Resolved References: {resolved_references}
            
            Identify the required operation(s) and explain your reasoning.""",
            context=""
        )

        # Step 4: Execution (Conditional Branching)
        if "arithmetic" in problem_analysis.lower():
            result = await self.generate(
                instruction=f"""Perform the arithmetic operation identified:
                Operation: {operation_identification}
                Entities: {entities}""",
                context=""
            )
        elif "counting" in problem_analysis.lower():
            result = await self.generate(
                instruction=f"""Count the specified entities or events:
                Operation: {operation_identification}
                Entities: {entities}""",
                context=""
            )
        elif "comparison" in problem_analysis.lower():
            result = await self.generate(
                instruction=f"""Compare the specified entities or values:
                Operation: {operation_identification}
                Entities: {entities}""",
                context=""
            )
        elif "span extraction" in problem_analysis.lower():
            result = await self.generate(
                instruction=f"""Extract the exact text span requested:
                Operation: {operation_identification}
                Entities: {entities}""",
                context=""
            )
        else:  # Multi-step
            intermediate_steps = await asyncio.gather(
                self.generate(instruction="Execute first operation...", context=operation_identification),
                self.generate(instruction="Execute second operation...", context=operation_identification)
            )
            result = await self.ensemble(
                instruction="Synthesize results from multiple steps into final answer",
                contexts_list=intermediate_steps
            )

        # Step 5: Answer Formatting
        formatted_answer = await self.generate(
            instruction=f"""Format the result appropriately:
            Result: {result}
            Expected format: Number, date, or exact text span""",
            context=""
        )

        return formatted_answer