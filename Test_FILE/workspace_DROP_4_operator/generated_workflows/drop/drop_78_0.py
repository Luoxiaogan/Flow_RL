# Workflow ID: drop_78_0
# Benchmark: drop
# Data Indices: [124, 151]

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

        # Step 1: Analyze problem structure and classify
        analysis = await self.generate(
            instruction="""Analyze the problem:
            - Identify key entities, numbers, and relationships in the passage.
            - Classify the question type (arithmetic, counting, comparison, span extraction).
            - Outline potential solution strategies.
            Provide structured analysis.""",
            context=""
        )

        # Step 2: Extract information and resolve references (parallel fork)
        entities, numbers, relationships = await asyncio.gather(
            self.generate(
                instruction="""Extract all named entities (people, places, organizations):
                Format as a list with descriptions.""",
                context=""
            ),
            self.generate(
                instruction="""Extract all numbers and their contexts:
                Format as a list with descriptions.""",
                context=""
            ),
            self.generate(
                instruction="""Identify relationships between entities:
                Format as a list of connections.""",
                context=""
            )
        )

        # Resolve references
        resolved_references = await self.generate(
            instruction=f"""Resolve pronouns and partial names in the question:
            Question: {self.problem_text}
            Entities: {entities}
            Relationships: {relationships}
            Provide resolved references.""",
            context=analysis
        )

        # Step 3: Identify and execute operations (conditional branch)
        if "arithmetic" in analysis.lower():
            operation_result = await self.generate(
                instruction=f"""Perform arithmetic operations:
                Numbers: {numbers}
                Context: {resolved_references}
                Show all steps and validate intermediate results.""",
                context=analysis
            )
        elif "comparison" in analysis.lower():
            operation_result = await self.generate(
                instruction=f"""Compare values or events:
                Entities: {entities}
                Numbers: {numbers}
                Context: {resolved_references}
                Determine the relationship.""",
                context=analysis
            )
        elif "span extraction" in analysis.lower():
            operation_result = await self.generate(
                instruction=f"""Extract exact text span:
                Passage: {self.problem_text}
                Context: {resolved_references}
                Ensure the span matches the passage exactly.""",
                context=analysis
            )
        else:
            operation_result = await self.generate(
                instruction=f"""Solve using general reasoning:
                Entities: {entities}
                Numbers: {numbers}
                Relationships: {relationships}
                Context: {resolved_references}""",
                context=analysis
            )

        # Step 4: Generate and validate the final answer
        final_answer = await self.revise(
            instruction=f"""Generate the final answer:
            Operation Result: {operation_result}
            Ensure the answer matches the required format (number, date, or exact span).""",
            context=operation_result
        )

        return final_answer