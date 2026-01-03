# Workflow ID: drop_17_0
# Benchmark: drop
# Data Indices: [31, 138]

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

        # Step 1: Problem Analysis
        analysis = await self.generate(
            instruction="""Analyze the problem structure:
            - Identify entities (teams, players, etc.)
            - Extract numerical values and their contexts
            - Determine the required operation(s) (counting, arithmetic, comparison, span extraction)
            - Classify the problem type (numerical, logical, textual)""",
            context=""
        )

        # Step 2: Information Extraction (Parallel Processing)
        entities_task = self.generate(
            instruction="Extract all named entities and their roles from the passage.",
            context=analysis
        )
        numbers_task = self.generate(
            instruction="Extract all numerical values and their associated contexts.",
            context=analysis
        )
        references_task = self.generate(
            instruction="Resolve pronouns and partial names to their correct entities.",
            context=analysis
        )
        entities, numbers, references = await asyncio.gather(entities_task, numbers_task, references_task)

        # Combine extracted information into a unified context
        unified_context = f"Entities: {entities}\nNumbers: {numbers}\nReferences: {references}"

        # Step 3: Operation Identification and Execution
        operation = await self.generate(
            instruction=f"""Based on the question phrasing, identify the required operation(s):
            - Counting: Specify filtering criteria and counting logic
            - Arithmetic: Define calculation steps
            - Comparison: Specify comparison criteria
            - Span Extraction: Define exact text matching logic
            Unified Context: {unified_context}""",
            context=analysis
        )

        # Dynamically execute the identified operation
        result = await self.generate(
            instruction=f"""Execute the identified operation:
            Operation Details: {operation}
            Unified Context: {unified_context}""",
            context=unified_context
        )

        # Step 4: Validation and Refinement (Iterative Loop)
        for _ in range(3):  # Allow up to 3 refinement iterations
            validation = await self.generate(
                instruction=f"""Validate the result:
                - Check calculations for accuracy
                - Ensure extracted spans match the passage exactly
                - Resolve ambiguities or inconsistencies
                Current Result: {result}""",
                context=unified_context
            )
            if "error" in validation.lower():
                result = await self.revise(
                    instruction=f"""Refine the result based on validation feedback:
                    Feedback: {validation}
                    Current Result: {result}""",
                    context=result
                )
            else:
                break

        # Step 5: Final Synthesis
        final_answer = await self.ensemble(
            instruction="""Synthesize the final answer:
            - Ensure the answer matches the expected format (number, date, or exact text span)
            - Select the most appropriate solution if multiple options exist""",
            contexts_list=[result, unified_context]
        )

        return final_answer