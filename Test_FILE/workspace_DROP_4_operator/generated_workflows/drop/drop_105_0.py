# Workflow ID: drop_105_0
# Benchmark: drop
# Data Indices: [104, 188]

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

        # Step 1: Initial Analysis
        analysis = await self.generate(
            instruction="""Analyze the problem:
            1. Classify the problem type (numerical, logical, textual).
            2. Identify key components (entities, numbers, relationships).
            3. Determine the expected answer format.
            Provide structured output.""",
            context=""
        )

        # Step 2: Entity Extraction and Reference Resolution
        entities_task = self.generate(
            instruction="Extract all named entities, numbers, and relationships from the passage.",
            context=""
        )
        references_task = self.generate(
            instruction="Resolve pronouns and partial names to their correct entities.",
            context=analysis
        )
        entities, references = await asyncio.gather(entities_task, references_task)

        refined_references = await self.revise(
            instruction="Refine reference resolution by analyzing context and relationships.",
            context=f"{entities}\n{references}"
        )

        # Step 3: Operation Identification
        operation_identification = await self.generate(
            instruction=f"""Based on the question and extracted information:
            {refined_references}
            
            Identify the required operation(s):
            - Arithmetic (addition, subtraction, etc.)
            - Counting
            - Comparison
            - Span extraction
            Provide clear reasoning.""",
            context=analysis
        )

        # Step 4: Operation Execution
        operation_tasks = []
        if "addition" in operation_identification.lower():
            operation_tasks.append(self.generate(
                instruction="Perform addition using the extracted numbers.",
                context=refined_references
            ))
        if "subtraction" in operation_identification.lower():
            operation_tasks.append(self.generate(
                instruction="Perform subtraction using the extracted numbers.",
                context=refined_references
            ))
        if "counting" in operation_identification.lower():
            operation_tasks.append(self.generate(
                instruction="Count occurrences of the specified entity or event.",
                context=refined_references
            ))
        if "comparison" in operation_identification.lower():
            operation_tasks.append(self.generate(
                instruction="Compare the specified values and determine the result.",
                context=refined_references
            ))
        if "span extraction" in operation_identification.lower():
            operation_tasks.append(self.generate(
                instruction="Extract the exact text span matching the question.",
                context=refined_references
            ))

        operation_results = await asyncio.gather(*operation_tasks)

        final_result = await self.ensemble(
            instruction="Select the best result based on the question requirements.",
            contexts_list=operation_results
        )

        # Step 5: Answer Formatting and Validation
        formatted_answer = await self.revise(
            instruction="Format the answer according to the expected format (number, date, text span).",
            context=final_result
        )

        return formatted_answer