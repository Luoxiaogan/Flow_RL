# Workflow ID: drop_132_0
# Benchmark: drop
# Data Indices: [436, 12]

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
        import re

        # Step 1: Initial Analysis and Classification
        classification = await self.generate(
            instruction="""Classify this problem into one of the following types:
            - Arithmetic (addition, subtraction, etc.)
            - Counting (how many times, how many different, etc.)
            - Comparison (greater/longer, more, came first/last, etc.)
            - Span Extraction (who did, what was the name of, when did, etc.)
            Provide the classification and key indicators from the question.""",
            context=""
        )

        # Step 2: Entity and Relationship Extraction
        entities = await self.generate(
            instruction=f"""Extract all named entities, numbers, and relationships from the passage:
            Format as a structured list:
            - Entities: [names and roles]
            - Numbers: [values and what they represent]
            - Relationships: [connections between entities and numbers]""",
            context=classification
        )

        # Step 3: Reference Resolution
        resolved_references = await self.generate(
            instruction=f"""Resolve all pronouns and partial names in the question to specific entities from the passage:
            Passage: {self.problem_text}
            Question: Extracted question from classification step.
            Provide the resolved references.""",
            context=entities
        )

        # Step 4: Operation Execution
        operation_result = await self.generate(
            instruction=f"""Based on the problem classification and resolved references:
            Classification: {classification}
            Resolved References: {resolved_references}
            
            Perform the required operation(s) and compute the result.
            Ensure all steps are clearly documented.""",
            context=resolved_references
        )

        # Step 5: Validation and Refinement
        validated_result = await self.revise(
            instruction=f"""Validate the computed result against the expected format:
            - Numbers should be numeric only
            - Dates should follow standard formats
            - Text spans must match the passage exactly
            If any issues are found, refine the result accordingly.""",
            context=operation_result
        )

        return validated_result