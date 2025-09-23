# Workflow ID: drop_191_0
# Benchmark: drop
# Data Indices: [144, 130]

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

        # Phase 1: Information Extraction and Reference Resolution
        entities_extraction = await self.generate(
            instruction="""Extract all named entities, numbers, and relationships from the passage:
            - Entities: Names of people, places, organizations, etc.
            - Numbers: All numerical values and their context
            - Relationships: Connections between entities and actions
            Format as a structured list.""",
            context=""
        )

        resolved_references = await self.revise(
            instruction=f"""Resolve references in the question:
            - Map pronouns ('he', 'it') and partial names to specific entities
            - Ensure all references are unambiguous
            Passage entities: {entities_extraction}""",
            context=entities_extraction
        )

        # Phase 2: Question Classification and Strategy Selection
        question_classification = await self.generate(
            instruction="""Classify the question type:
            - Arithmetic: Involves addition, subtraction, multiplication, etc.
            - Counting: Requires counting occurrences or items
            - Comparison: Involves comparing values or quantities
            - Span Extraction: Requires extracting exact text spans
            Provide classification and reasoning.""",
            context=resolved_references
        )

        # Dynamically construct instructions based on classification
        if "arithmetic" in question_classification.lower():
            operation_instructions = """Identify and perform arithmetic operations:
            - Sum relevant numbers
            - Subtract as needed
            - Show all steps"""
        elif "counting" in question_classification.lower():
            operation_instructions = """Count occurrences:
            - Identify target entities or events
            - Count all instances
            - Ensure completeness"""
        elif "comparison" in question_classification.lower():
            operation_instructions = """Compare values:
            - Identify comparison targets
            - Determine greater/lesser or first/last
            - Justify result"""
        else:
            operation_instructions = """Extract exact text spans:
            - Match question phrasing to passage content
            - Ensure precision"""

        # Phase 3: Operation Execution
        operation_results = await asyncio.gather(
            self.generate(
                instruction=operation_instructions,
                context=resolved_references
            ),
            self.revise(
                instruction="Validate intermediate results for accuracy and completeness.",
                context=resolved_references
            )
        )

        # Phase 4: Final Answer Synthesis
        final_answer = await self.ensemble(
            instruction="""Synthesize results into a final answer:
            - Combine insights from all operations
            - Resolve ambiguities
            - Format answer appropriately (number, date, or text span)""",
            contexts_list=operation_results
        )

        return final_answer