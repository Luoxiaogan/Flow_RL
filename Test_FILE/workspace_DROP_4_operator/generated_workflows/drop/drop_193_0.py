# Workflow ID: drop_193_0
# Benchmark: drop
# Data Indices: [156, 41]

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
        
        # Step 1: Initial Analysis - Extract entities, numbers, and relationships
        initial_analysis = await self.generate(
            instruction="""Extract all named entities, numbers, and relationships from the passage:
            - Entities: Names, roles, places, events
            - Numbers: Values and their context
            - Relationships: How entities interact
            Format as structured lists.""",
            context=""
        )
        
        # Step 2: Parallel Processing - Resolve references and classify problem type
        entities_task = self.generate(
            instruction=f"""Resolve all pronouns and partial names in the question:
            Passage Context: {initial_analysis}
            Map references to specific entities.""",
            context=initial_analysis
        )
        operation_task = self.generate(
            instruction=f"""Classify the problem type and identify required operations:
            Question: What is being asked?
            Possible operations: Arithmetic, Comparison, Span Extraction.""",
            context=initial_analysis
        )
        entities_resolved, operation_classified = await asyncio.gather(entities_task, operation_task)
        
        # Step 3: Operation-Specific Subroutines
        if "arithmetic" in operation_classified.lower():
            result = await self.arithmetic_subroutine(entities_resolved, operation_classified)
        elif "comparison" in operation_classified.lower():
            result = await self.comparison_subroutine(entities_resolved, operation_classified)
        elif "span extraction" in operation_classified.lower():
            result = await self.span_extraction_subroutine(entities_resolved, operation_classified)
        else:
            result = await self.generate(
                instruction="Apply general problem-solving framework.",
                context=entities_resolved
            )
        
        # Step 4: Synthesis and Validation
        validated_result = await self.revise(
            instruction="Validate the result against the expected format (number, date, or text span).",
            context=result
        )
        
        return validated_result
    
    async def arithmetic_subroutine(self, entities, operation):
        calculation = await self.generate(
            instruction=f"""Perform the required arithmetic operation:
            Entities: {entities}
            Operation: {operation}
            Show all steps and maintain precision.""",
            context=""
        )
        return calculation
    
    async def comparison_subroutine(self, entities, operation):
        comparison = await self.generate(
            instruction=f"""Compare the relevant values:
            Entities: {entities}
            Operation: {operation}
            Determine greater/lesser, earlier/later, etc.""",
            context=""
        )
        return comparison
    
    async def span_extraction_subroutine(self, entities, operation):
        span = await self.generate(
            instruction=f"""Extract the exact text span that answers the question:
            Entities: {entities}
            Operation: {operation}
            Ensure the span matches the passage exactly.""",
            context=""
        )
        return span