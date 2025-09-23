# Workflow ID: drop_186_0
# Benchmark: drop
# Data Indices: [13, 450]

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

        # Step 1: Extract Entities and Relationships
        entities = await self.generate(
            instruction="""Extract all named entities, numbers, and relationships:
            - People: [names and roles]
            - Places: [locations and contexts]
            - Numbers: [values and what they represent]
            - Actions: [what happens and when]
            Format as a structured list.""",
            context=""
        )

        # Step 2: Resolve References and Identify Constraints
        resolved_references = await self.generate(
            instruction=f"""Resolve pronouns and partial names to specific entities:
            Entities: {entities}
            Also identify constraints and conditions mentioned in the passage.""",
            context=entities
        )

        # Step 3: Identify Required Operation(s)
        operation_identification = await self.generate(
            instruction=f"""Based on the question and the extracted information:
            Entities: {entities}
            Resolved References: {resolved_references}
            Identify the required operation(s): addition, subtraction, counting, comparison, or span extraction.
            Provide reasoning for your choice.""",
            context=resolved_references
        )

        # Step 4: Execute Operations in Parallel
        operation_results = await asyncio.gather(
            self.generate(
                instruction=f"""Perform arithmetic operations (addition, subtraction, etc.):
                Entities: {entities}
                Resolved References: {resolved_references}
                Operation: {operation_identification}""",
                context=resolved_references
            ),
            self.generate(
                instruction=f"""Extract relevant text spans:
                Entities: {entities}
                Resolved References: {resolved_references}
                Operation: {operation_identification}""",
                context=resolved_references
            ),
            self.generate(
                instruction=f"""Perform comparison or sorting:
                Entities: {entities}
                Resolved References: {resolved_references}
                Operation: {operation_identification}""",
                context=resolved_references
            )
        )

        # Step 5: Ensemble to Select Best Result
        final_answer = await self.ensemble(
            instruction="""Select the most accurate and relevant result:
            Consider:
            - Does it match the expected format?
            - Is it consistent with the passage?
            - Does it answer the question fully?""",
            contexts_list=operation_results
        )

        # Step 6: Validate and Refine Final Answer
        refined_answer = await self.revise(
            instruction="""Validate the final answer:
            - Ensure correct format (number, date, or text span)
            - Cross-check with the passage
            - Correct any inconsistencies""",
            context=final_answer
        )

        return refined_answer