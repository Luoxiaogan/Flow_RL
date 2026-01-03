# Workflow ID: drop_93_0
# Benchmark: drop
# Data Indices: [384, 335]

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

        # Phase 1: Parallel Extraction of Entities, Numbers, and Relationships
        entities_task = self.generate(
            instruction="""Extract all named entities, numbers, and relationships:
            - People: [names and roles]
            - Places: [locations and contexts]
            - Numbers: [values and what they represent]
            - Actions: [what happens and when]""",
            context=""
        )
        question_type_task = self.generate(
            instruction="""Classify the question type:
            - Arithmetic (addition, subtraction, etc.)
            - Counting (how many times, how many different, etc.)
            - Comparison (greater than, less than, etc.)
            - Span Extraction (who did, what was, etc.)""",
            context=""
        )
        entities, question_type = await asyncio.gather(entities_task, question_type_task)

        # Phase 2: Reference Resolution
        resolved_references = await self.generate(
            instruction=f"""Resolve all pronouns and partial references in the question:
            - Use the following entities as context: {entities}
            - Ensure each reference maps to a specific entity or number in the passage""",
            context=question_type
        )

        # Phase 3: Operation Identification and Execution
        if "arithmetic" in question_type.lower():
            result = await self.generate(
                instruction=f"""Perform the required arithmetic operation:
                - Use the resolved references: {resolved_references}
                - Show all calculation steps
                - Present the final numerical answer""",
                context=entities
            )
        elif "counting" in question_type.lower():
            result = await self.generate(
                instruction=f"""Count the required instances:
                - Use the resolved references: {resolved_references}
                - Identify all relevant occurrences in the passage
                - Present the total count""",
                context=entities
            )
        elif "comparison" in question_type.lower():
            result = await self.generate(
                instruction=f"""Compare the specified values:
                - Use the resolved references: {resolved_references}
                - Determine which value is greater/less/equal
                - Present the comparison result""",
                context=entities
            )
        elif "span extraction" in question_type.lower():
            result = await self.generate(
                instruction=f"""Extract the exact text span that answers the question:
                - Use the resolved references: {resolved_references}
                - Ensure the span matches the passage exactly
                - Present the extracted span""",
                context=entities
            )
        else:
            result = await self.generate(
                instruction="Apply general problem-solving framework...",
                context=entities
            )

        # Phase 4: Iterative Refinement and Validation
        for _ in range(3):  # Allow up to 3 refinement iterations
            validation = await self.generate(
                instruction=f"""Validate the result:
                - Check if the answer matches the expected format
                - Verify calculations or span extraction
                - Flag any issues""",
                context=result
            )
            if "error" in validation.lower():
                result = await self.revise(
                    instruction=f"""Fix issues identified during validation:
                    - Issues: {validation}
                    - Correct the result accordingly""",
                    context=result
                )
            else:
                break

        return result