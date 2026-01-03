# Workflow ID: drop_129_0
# Benchmark: drop
# Data Indices: [108, 403]

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

        # Step 1: Extract all entities, numbers, and relationships
        entities_extraction = await self.generate(
            instruction="""Extract all named entities, numbers, and relationships from the passage. 
            Format as a structured list with categories:
            - People: [names and roles]
            - Places: [locations and contexts]
            - Numbers: [values and what they represent]
            - Actions: [what happens and when]""",
            context=""
        )

        # Step 2: Classify the question type and identify required operation
        question_analysis = await self.generate(
            instruction=f"""Analyze the question and classify its type:
            - Is it numerical, logical, or textual?
            - Does it require arithmetic (addition, subtraction, etc.)?
            - Does it involve counting, comparison, or span extraction?
            Passage entities for reference: {entities_extraction}""",
            context=""
        )

        # Step 3: Resolve references and map question to passage entities
        reference_resolution = await self.generate(
            instruction=f"""Resolve all references in the question to specific entities in the passage:
            - Replace pronouns with full names
            - Clarify partial references
            Passage entities for reference: {entities_extraction}
            Question analysis: {question_analysis}""",
            context=question_analysis
        )

        # Step 4: Perform the required operation(s)
        # Parallelize arithmetic and span extraction if needed
        arithmetic_task = asyncio.create_task(
            self.generate(
                instruction=f"""Perform any required arithmetic operations:
                - Addition, subtraction, counting, etc.
                Use the following data:
                Passage entities: {entities_extraction}
                Reference resolution: {reference_resolution}""",
                context=reference_resolution
            )
        )

        span_extraction_task = asyncio.create_task(
            self.generate(
                instruction=f"""Extract the exact text span from the passage that answers the question:
                - Match the span exactly as it appears in the passage
                Passage entities: {entities_extraction}
                Reference resolution: {reference_resolution}""",
                context=reference_resolution
            )
        )

        arithmetic_result, span_extraction_result = await asyncio.gather(arithmetic_task, span_extraction_task)

        # Step 5: Select the final answer using ensemble
        final_answer = await self.ensemble(
            instruction="""Select the most appropriate answer:
            - If the question requires a numerical answer, choose the arithmetic result.
            - If the question requires a text span, choose the span extraction result.
            - Handle cases where both are valid.""",
            contexts_list=[arithmetic_result, span_extraction_result]
        )

        # Step 6: Format the answer to match expected output
        formatted_answer = await self.revise(
            instruction="""Format the answer to match the expected output:
            - For numerical answers, strip unnecessary text and include units if applicable.
            - For text spans, ensure exact matching with the passage.""",
            context=final_answer
        )

        return formatted_answer