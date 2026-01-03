# Workflow ID: drop_90_0
# Benchmark: drop
# Data Indices: [461, 175]

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

        # Step 1: Initial Analysis - Extract entities and relationships
        entities_analysis = await self.generate(
            instruction="""Extract all named entities, numbers, and relationships from the passage:
            - Categorize entities (people, places, numbers, actions)
            - Identify temporal markers (first, second, third quarter, etc.)
            - Map relationships between entities (who did what, when, and where)""",
            context=""
        )

        # Step 2: Identify Operation Type and Constraints
        operation_analysis = await self.generate(
            instruction=f"""Analyze the question to identify:
            - The type of operation required (arithmetic, counting, comparison, span extraction)
            - Key constraints or conditions (e.g., 'first', 'longest', 'total')
            Passage Entities: {entities_analysis}""",
            context=""
        )

        # Step 3: Parallel Processing - Reference Resolution and Operation Setup
        reference_resolution, operation_setup = await asyncio.gather(
            self.generate(
                instruction=f"""Resolve references in the question to specific entities in the passage:
                - Replace pronouns and partial names with full entity names
                Passage Entities: {entities_analysis}""",
                context=operation_analysis
            ),
            self.generate(
                instruction=f"""Set up the operation based on its type:
                - For arithmetic: Identify numbers and required calculations
                - For span extraction: Identify candidate text spans
                - For comparison: Identify values to compare
                Operation Analysis: {operation_analysis}""",
                context=entities_analysis
            )
        )

        # Step 4: Conditional Branching - Execute Operation-Specific Logic
        if "arithmetic" in operation_analysis.lower():
            result = await self.generate(
                instruction=f"""Perform the required arithmetic operation:
                - Show all calculation steps
                - Validate intermediate results
                - Present final answer with appropriate units
                Operation Setup: {operation_setup}""",
                context=reference_resolution
            )
        elif "span extraction" in operation_analysis.lower():
            result = await self.generate(
                instruction=f"""Extract the exact text span from the passage:
                - Match the span to the question's requirements
                - Resolve ambiguities if multiple spans are possible
                Operation Setup: {operation_setup}""",
                context=reference_resolution
            )
        elif "comparison" in operation_analysis.lower():
            result = await self.generate(
                instruction=f"""Compare the identified values:
                - Determine which value satisfies the condition (greater, longer, earlier, etc.)
                - Validate the comparison logic
                Operation Setup: {operation_setup}""",
                context=reference_resolution
            )
        else:
            result = await self.generate(
                instruction=f"""Apply general reasoning to solve the problem:
                - Use passage entities and resolved references
                - Follow the question's constraints
                Operation Setup: {operation_setup}""",
                context=reference_resolution
            )

        # Step 5: Ensemble Synthesis - Validate and Select Best Answer
        final_answer = await self.ensemble(
            instruction="""Evaluate the candidate answers:
            - Ensure they match the question's requirements
            - Select the most plausible answer based on evidence from the passage""",
            contexts_list=[result, reference_resolution, operation_setup]
        )

        # Step 6: Final Revision - Format the Answer
        formatted_answer = await self.revise(
            instruction="""Ensure the answer matches the expected format:
            - Numbers should include units if applicable
            - Text spans should match the passage exactly
            - Dates should follow standard formats""",
            context=final_answer
        )

        return formatted_answer